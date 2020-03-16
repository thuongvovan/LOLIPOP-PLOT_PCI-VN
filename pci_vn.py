#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
from funtion import *

#%%
# Các thông tin của bảng xếp hạng chỉ số năng lực cạnh tranh cấp tỉnh công bố tại website: http://pcivietnam.org
url = 'http://pcivietnam.org/bang-xep-hang/?khu_vuc={}&chi_so={}&nam={}'
nam = range(2006,2018+1)
khu_vuc = 0
chi_so = 'pci'

#%%
# Lấy dữ liệu về
pci_vn = lay_pci_vn(url, nam, khu_vuc, chi_so)

#%%
# Lưu lại để sử dụng lần sau
# pci_vn.to_csv('data/pci_vn.csv')
# pci_vn = pd.read_csv('data/pci_vn.csv', index_col= 0)

#%%
# Cột Nhóm xếp hạng không đầy đủ -> không sử dụng được -> xoá
pci_vn = pci_vn.drop(columns = 'Nhóm xếp hạng')
# Đổi tên biến
pci_vn = pci_vn.rename(columns = {'Địa phương': 'dia_phuong', 'Điểm số PCI': 'pci', 'Xếp hạng': 'xep_hang'})
# Làm tròn chỉ số PCI về 2 chữ số thập thân
pci_vn['pci'] = pci_vn['pci'].apply(lambda x: round(x, 2))

#%%
# Kiểm tra danh sách địa phương thì danh sách địa phương có đến 65 giá trị
# => Có 2 địa phương bị ghi sai lỗi chính tả (hoặc cách ghi không đồng nhất): Da Nang và Ha Nam
# Chuẩn hoá tên hai địa phương viết không đồng nhất
pci_vn.loc[pci_vn['dia_phuong'] == 'Da Nang', 'dia_phuong'] = 'Đà Nẵng'
pci_vn.loc[pci_vn['dia_phuong'] == 'Ha Nam', 'dia_phuong'] = 'Hà Nam'

#%%
# Xác định xong bảng giá trị khởi đầu.
pci_vn_dau = xac_dinh_khoi_dau(pci_vn)
pci_vn_dau.rename(columns = {'pci': 'pci_khoi_dau', 'nam': 'nam_khoi_dau', 'xep_hang': 'xep_hang_khoi_dau'}, inplace= True)
# Lúc này nhận thấy bảng giá trị khởi đầu chính là năm 2006.
# Chỉ số PCI đã thu thập từ năm 2005 trên 42 tỉnh thành tuy nhiên giá trị năm 2015 lại không được đưa vào bảng xếp hạng.
# Tuy vậy funtion này cũng củng cố thêm niềm tin bảng giá trị này chính là bảng giá trị khởi đầu.

#%%
# Tạo cột số thứ hạng thay đổi theo năm và điểm thay đổi theo từng năm
pci_vn = bo_sung_thay_doi_theo_nam(pci_vn)

#%%
thay_doi_toi_da = tim_thay_doi_hang_toi_da_theo_nam(pci_vn)

#%%
# Xác định tốc độ trượt trên trục thứ hạng (trục y)
# bằng cách nhân với giá trị tuyệt đối của thương: số hạng thay đổi tối đa / số hạng thay đổi của nước hiện tại

# Thêm cột thay đổi tối đa mỗi năm
pci_vn = pci_vn.join(other= thay_doi_toi_da, on= 'nam')

# Cột tốc độ trượt
pci_vn['toc_do_truot'] = pci_vn['thay_doi_toi_da'] / pci_vn['thay_doi_hang_theo_nam'].abs()

#%%
# Điều chỉnh giá trị của tốc độ đối với năm 2006 bằng 0
pci_vn['toc_do_truot'].loc[(pci_vn['thay_doi_hang_theo_nam'] == 0) & (pci_vn['nam'] == 2006)] = 0

#%%
# Gán các giá trị dương vô cùng bằng nan
pci_vn['toc_do_truot'].loc[(pci_vn['toc_do_truot'] == np.inf)] = np.nan

#%%
# Ở mỗi năm còn lại các giá trị không thay đổi hạng được gán tốc độ bằng tốc độ tối đa
for i in pci_vn.nam.unique():
    pci_vn['toc_do_truot'].loc[(pci_vn['thay_doi_hang_theo_nam'] == 0) & (pci_vn['nam'] == i)] = pci_vn['toc_do_truot'].loc[pci_vn['nam'] == i].max()

#%%
# Tạo biến PCI và biến xếp hạng riêng để làm giá trị chạy
# Biến PCI và biến xếp hạng gốc giữ lại nhằm lấy giá trị hiển thị
pci_vn['pci_bien_chay'] = pci_vn['pci']
pci_vn['xep_hang_bien_chay'] = pci_vn['xep_hang']

#%%
# Làm mượt dữ liệu
pci_vn_da_muot = pd.DataFrame()
for i in pci_vn['dia_phuong'].unique():
    data = pci_vn[pci_vn['dia_phuong'] == i]
    data = lam_muot_du_lieu(data=data, var=['pci_bien_chay', 'xep_hang_bien_chay'], by='nam', fps=80)
    pci_vn_da_muot = pci_vn_da_muot.append(data)

#%%
# Thêm các cột thông tin lúc khởi đầu thu thập vào dataframe
pci_vn_da_muot = pci_vn_da_muot.merge(pci_vn_dau, on= 'dia_phuong')

#%%
# Chuyển cột xếp hạng thành giá trị âm để đẩy cột hạng cao nhất lên trên
pci_vn_da_muot['xep_hang_bien_chay'] = pci_vn_da_muot['xep_hang_bien_chay'] * -1

#%%
# Tạo các giá trị trục cho biểu đồ
xmin = pci_vn_da_muot[['pci_khoi_dau', 'pci_bien_chay']].min().min()
xmin = xmin * 0.75
xmax = pci_vn_da_muot[['pci_khoi_dau', 'pci_bien_chay']].max().max()
xmax = xmax * 1.1

#%%
fps = pci_vn_da_muot['fps'].unique()
fps = np.sort(fps)

list_plot_array = []
i = 0
for f in fps:
    data = pci_vn_da_muot[pci_vn_da_muot['fps'] == f]
    plot_data = ve_lollipop_plot(data, xmin, xmax)
    list_plot_array.append(plot_data)
    i += 1
    print('Hình thứ:', i, '/', len(fps))
    if f.split('-')[1] == '80':
        if f.split('-')[1] == '2006':
            so_vong = 120
        else:
            so_vong = 60
        for j in range(so_vong):
            list_plot_array.append(plot_data)

# %% RENDER VIDEO
height, width, layers = list_plot_array[0].shape
size = (width, height)
video_name = '/content/gdrive/My Drive/Colab Notebooks/PCI_VN/Lollipop_PCI_VN-2006-2018.avi'
video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
for i in range(len(list_plot_array)):
    video.write(list_plot_array[i])
video.release()
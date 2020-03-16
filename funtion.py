
#%%
# Funtion lấy một bảng với các thông tin năm, khu vực và chỉ số
# Trường hợp này lấy 1 bảng là thông tin chỉ số PCI trong một năm
def lay_pci_1_nam(url, nam, khu_vuc, chi_so):
    data = pd.read_html(url.format(khu_vuc, chi_so, nam))
    data = data[0]
    return data

#%%
# Funtipn lấy và ghép chỉ số PCI của tất cả các năm
def lay_pci_vn(url, nam, khu_vuc, chi_so):
    pci = pd.DataFrame()
    for nam in nam:
        data = lay_pci_1_nam(url, nam, khu_vuc, chi_so)
        data['nam'] = nam
        pci = pci.append(data)
    return pci

#%%
# Funtion xác định bảng giá trị đầu tiên thu thập của các địa phương
# Trong lollipop plot dự định vẽ 2 điểm cho mỗi địa phương:
# - Điểm đầu tiên bắt đầu đánh giá
# - Điểm của năm hiện tại
# Tuy nhiên các địa phương có thời điểm bắt đầu đánh giá khác nhau
# Vì vậy cần xác định bẳng giá trị đầu tiên đánh giá và năm đầu tiên đánh giá (gọi là bang gia tri khoi dau)
def xac_dinh_khoi_dau(data):
    data_khoi_dau = pd.DataFrame()
    for i in data['dia_phuong'].unique():
        data_dia_phuong = data[data['dia_phuong'] == i]
        nam_dau = data_dia_phuong['nam'].min()
        gia_tri_dau = data_dia_phuong[data_dia_phuong['nam'] == nam_dau]
        data_khoi_dau = data_khoi_dau.append(gia_tri_dau)
    return data_khoi_dau
#%% -----------------
# Xác số hạng thay đổi mỗi năm của mỗi nước
def xac_dinh_thay_doi_thu_hang_1_dia_phuong(data_dia_phuong):
    data = data_dia_phuong.sort_values(by= 'nam', ascending=True).reset_index(drop=True)
    for i in range(data.shape[0]):
        if i == 0:
            data['thay_doi_hang_theo_nam'] = 0
            data['thay_doi_diem_theo_nam'] = 0
        else:
            thay_doi_hang = data['xep_hang'].iloc[i] - data['xep_hang'].iloc[i-1]
            data['thay_doi_hang_theo_nam'].iloc[i] = thay_doi_hang

            thay_doi_diem = data['pci'].iloc[i] - data['pci'].iloc[i-1]
            data['thay_doi_diem_theo_nam'].iloc[i] = thay_doi_diem
    return data
#%%
def bo_sung_thay_doi_theo_nam(data):
    pci_vn = pd.DataFrame()
    dia_phuong = data['dia_phuong'].unique()
    for i in dia_phuong:
        df_dia_phuong = data[data['dia_phuong'] == i]
        df_dia_phuong = xac_dinh_thay_doi_thu_hang_1_dia_phuong(df_dia_phuong)
        pci_vn = pci_vn.append(df_dia_phuong)
    return pci_vn.sort_values(by= ['nam', 'xep_hang'], ascending=True).reset_index(drop=True)

#%%
# Xác định hạng thay đổi cao nhất trong năm
def tim_thay_doi_hang_toi_da_theo_nam(data):
    data = data[['nam', 'thay_doi_hang_theo_nam']]
    data = data.rename( columns = {'thay_doi_hang_theo_nam': 'thay_doi_toi_da'})
    data['thay_doi_toi_da'] = data['thay_doi_toi_da'].abs()
    data = data.groupby('nam').max()
    return data

#%%
# Funtion chia nhỏ các quãng thay đổi của chỉ số.
# Gọi việc này là làm mượt số liệu cho một địa phương
def lam_muot_du_lieu(data, var, by, fps, ascending=True):
    # data: là bộ dữ liệu
    # var: là cột số cần làm mượt. 1 cột hoặc 1 list các cột
    # by: là cột cố định trong khi làm mượt
    # fps: số  lần chia nhỏ dữ liệu (1 lần là 1 khung hình)
    # ==> Hàm này sẽ làm mượt dữ liệu cột bar theo từng bước thay đổi của cột by,
    # ==> mỗi bước thay đổi của cột by sẽ chia nhỏ cột var thành fps lần thay đổi (VD: từ 1-5 chia nhỏ thành: 1-2-3-4-5)
    # ==> data sẽ được bổ sung thêm cột fps - sẽ là cột để làm giá trị chạy cho biểu đồ.
    # ==> cột var được tạo thêm các giá trị trung gian để làm mượt giữ liệu

    # Tạo list rỗng để chứa các giá trị
    list_of_dic = []
    # danh sách các cột không thay đổi
    column_names = list(data.columns.values)
    if type(var) != list:
        var = [var]
    for i in var:
        column_names.remove(i)
    # sắp xếp dữ liệu theo cột by cố định
    data = data.sort_values(by=by, ascending=ascending).reset_index(drop=True)

    # Vòng lặp đầu tiên đi từ đầu đến cuối bộ dữ liệu
    # Lưu ý: dữ liệu cần được sắp
    for i in range(data.shape[0]):
        if i == 0:
            # Tại hàng đầu tiên của dữ liệu
            dic = {}
            for c in column_names:
                dic[c] = data[c][i]
            for v in var:
                dic[v] = data[v][i]
            dic['fps'] = str(data[by][i]) + '-' + str(fps)
            list_of_dic.append(dic)
        else:
            # Tại các dòng tiếp theo
            # Lặp để tạo thêm các số liệu trung gian nhằm tăng độ mượt
            # Với số khung hình (fps) được chọn
            for j in range(fps):
                #
                dic = {}
                for c in column_names:
                    dic[c] = data[c][i]
                for v in var:
                    phan_du = data[v][i] - data[v][i - 1] #
                    value = data[v][i - 1] + (j/(fps-1)) * phan_du * data['toc_do_truot'][i]
                    if phan_du > 0:
                        if value >= data[v][i]:
                            value = data[v][i]
                    if phan_du < 0:
                        if value <= data[v][i]:
                            value = data[v][i]
                    dic[v] = value
                dic['fps'] = str(data[by][i]) + '-' + '0' * (len(str(fps)) - len(str(j + 1))) + str(j + 1)
                list_of_dic.append(dic)
    return pd.DataFrame(list_of_dic)


#%%
def ve_lollipop_plot(data, xmin, xmax):
    xmean = xmin + (xmax - xmin)/2
    plt.style.use('dark_background')
    fig = plt.figure(figsize  = (5, 7), dpi = 150)
    plt.subplot(111)
    mau_line = 'whitesmoke'
    mau_pci = 'peru'
    mau_pci_khoi_dau = 'skyblue'
    size_tieu_de = 10
    size_diem = 8
    size_pci = 4.5
    mau_tieu_de = 'w'
    mau_giam = 'indianred'
    mau_tang = 'seagreen'

    # Điểm PCI năm khởi đầu
    plt.scatter(x = data['pci_khoi_dau'], y = data['xep_hang_bien_chay'],
                color= mau_pci_khoi_dau, alpha=1, s = size_diem, label='Năm 2006')

    # Line nối và pci chạy loại trừ năm 2006
    if data['fps'].iloc[0].split('-')[0] != '2006':
        plt.hlines(y=data['xep_hang_bien_chay'],
                   xmin= data['pci_khoi_dau'], xmax=data['pci_bien_chay'],
                   color= mau_line, alpha=0.6)
        # Điểm PCI năm hiện tại
        plt.scatter(x = data['pci_bien_chay'], y = data['xep_hang_bien_chay'],
                    color= mau_pci, alpha=1, s = size_diem,
                    label='Năm' + str(data['nam'].iloc[0]))


    # Cố định trục
    plt.xlim((xmin, xmax+2))
    plt.ylim((-64, 2))

    # Canh chỉnh tiêu đề
    plt.title('CHỈ SỐ NĂNG LỰC CẠNH TRANH CẤP TỈNH (PCI)',
              fontweight="bold", fontsize= size_tieu_de, color= mau_tieu_de)

    if data['nam'].iloc[0] != 2006:
        plt.text(x = xmean - 2, y = 1, s = str(data['nam_khoi_dau'].iloc[0]),
                 color= mau_pci_khoi_dau, va="center", ha="right", fontweight="bold", fontsize= size_tieu_de)
        plt.scatter(x= xmean -2 -8 , y= 1.1,
                    color=mau_pci_khoi_dau, alpha=1, s=size_diem * 7, label='Năm 2006')
        plt.text(x = xmean , y = 1, s = '-',
                 va="center", ha="center", fontweight="bold", fontsize= size_tieu_de, color= mau_tieu_de)
        plt.text(x = xmean + 2, y = 1, s = str(data['nam'].iloc[0]),
                 color= mau_pci, va="center", ha="left", fontweight="bold", fontsize= size_tieu_de)
        plt.scatter(x= xmean +2 +8 , y= 1.1,
                    color=mau_pci, alpha=1, s=size_diem * 7, label='Năm' + str(data['nam'].iloc[0]))
    else:
        plt.text(x = xmean, y = 1, s = str(data['nam_khoi_dau'].iloc[0]),
                 color= mau_pci_khoi_dau, va="center", ha="center", fontweight="bold", fontsize= size_tieu_de)
        plt.scatter(x= xmean -8 , y= 1.1,
                    color=mau_pci_khoi_dau, alpha=1, s=size_diem * 7, label='Năm 2006')

    # Vẽ tên địa phương và xếp hạng
    # Nếu tăng hạng màu xanh, giảm màu đỏ và giữ nguyên hạng là màu trắng (so với 2016)
    for i in range(data.shape[0]):
        # Điểm PCI

        if data['pci_bien_chay'].iloc[i] >= data['pci_khoi_dau'].iloc[i]:
            toa_do_x_pci_khoi_dau = data['pci_khoi_dau'].iloc[i] - 1
            ha_pci_khoi_dau = 'right'
            toa_do_x_pci_hien_tai = data['pci_bien_chay'].iloc[i] + 1
            ha_pci_hien_tai = 'left'
        else:
            toa_do_x_pci_khoi_dau = data['pci_khoi_dau'].iloc[i] + 1
            ha_pci_khoi_dau = 'left'
            toa_do_x_pci_hien_tai = data['pci_bien_chay'].iloc[i] - 1
            ha_pci_hien_tai = 'right'

        # Line mờ hiệu ứng dễ nhìn
        diem_ket_line_mo_1 = min(toa_do_x_pci_khoi_dau, toa_do_x_pci_hien_tai) - 4.5
        diem_ket_line_mo_1 = diem_ket_line_mo_1 if diem_ket_line_mo_1 > (1.2 * xmin) else (1.2 * xmin)
        plt.hlines(y=data['xep_hang_bien_chay'].iloc[i],
                   xmin= 1.2 * xmin, xmax= diem_ket_line_mo_1,
                   linewidths = 0.3, linestyles = 'dotted', color=mau_line, alpha=0.45)

        # Điểm PCI năm khởi đầu
        plt.text(x= toa_do_x_pci_khoi_dau, y= data['xep_hang_bien_chay'].iloc[i],
                 s= str(data['pci_khoi_dau'].iloc[i]),
                 color= mau_pci_khoi_dau, va="center", ha= ha_pci_khoi_dau, fontsize= size_pci, stretch='ultra-condensed')

        # Điểm PCI năm hiện tại
        if data['fps'].iloc[0].split('-')[0] != '2006':
            plt.text(x= toa_do_x_pci_hien_tai, y= data['xep_hang_bien_chay'].iloc[i],
                     s= str(data['pci'].iloc[i]),
                    color= mau_pci, va="center", ha= ha_pci_hien_tai, fontsize= size_pci, stretch='ultra-condensed')

        # Xếp hạng
        str_xep_hang = str(data['xep_hang'].iloc[i])
        plt.text(x=xmin * 0.82, y=data['xep_hang'].iloc[i] * -1,
                 s=str_xep_hang + '. ',
                 color=mau_tieu_de, va="center", ha="right", fontsize= 5,
                 fontweight="bold", stretch='ultra-condensed', alpha=0.7)

        # Điều kiện để xuất hiện thay đổi thứ bậc số với năm trước
        str_dia_phuong = str(data['dia_phuong'].iloc[i])
        mau_chu = mau_tieu_de
        if data['thay_doi_hang_theo_nam'].iloc[i] < 0:
            mau_chu = mau_tang
        elif data['thay_doi_hang_theo_nam'].iloc[i] > 0:
            mau_chu = mau_giam

        plt.text(x=xmin * 0.85, y=data['xep_hang_bien_chay'].iloc[i],
                s= str_dia_phuong,
                color=mau_chu, va="center", ha="left", fontsize= size_pci,
                fontweight="bold", stretch='ultra-condensed', alpha=0.7)

        xuat_hien_tang_hang = data['pci'].iloc[i] == data['pci_bien_chay'].iloc[i]
        khac_nam_2006 = data['fps'].iloc[0].split('-')[0] != '2006'
        if khac_nam_2006:
            if xuat_hien_tang_hang:
                # Thay đổi màu chữ của tăng giảm thứ hạng so với năm trước
                if data['thay_doi_hang_theo_nam'].iloc[i] < 0:
                    str_thay_doi_hang_theo_nam = '+' + str(data['thay_doi_hang_theo_nam'].iloc[i] * -1)
                elif data['thay_doi_hang_theo_nam'].iloc[i] == 0:
                    str_thay_doi_hang_theo_nam = ''
                else:
                    str_thay_doi_hang_theo_nam = str(data['thay_doi_hang_theo_nam'].iloc[i] * -1)
            else:
                str_thay_doi_hang_theo_nam = ''

            plt.text(x=xmin * 0.72, y=data['xep_hang_bien_chay'].iloc[i],
                    s= str_thay_doi_hang_theo_nam,
                    color=mau_chu, va="center", ha="right", fontsize= size_pci,
                    fontweight="bold", stretch='ultra-condensed', alpha=0.7)

        # Thay đổi màu chữ của tăng giảm thứ hạng so với 2006
        if khac_nam_2006:
            if xuat_hien_tang_hang:
                thay_doi_xep_hang_vs_2006 = data['xep_hang'].iloc[i] - data['xep_hang_khoi_dau'].iloc[i]
                thay_doi_xep_hang_vs_2006 = thay_doi_xep_hang_vs_2006 * -1

                # Thay đổi màu chữ của tăng giảm thứ hạng so với 2006
                if thay_doi_xep_hang_vs_2006 < 0:
                    str_thay_doi_xep_hang = str(thay_doi_xep_hang_vs_2006)
                    mau_thay_doi_xep_hang = mau_giam
                elif thay_doi_xep_hang_vs_2006 == 0:
                    str_thay_doi_xep_hang = '-'
                    mau_thay_doi_xep_hang = mau_tieu_de
                else:
                    str_thay_doi_xep_hang = '+' + str(thay_doi_xep_hang_vs_2006)
                    mau_thay_doi_xep_hang = mau_tang
            else:
                str_thay_doi_xep_hang = '-'
                mau_thay_doi_xep_hang = mau_tieu_de

            plt.text(x=xmax + 2, y=data['xep_hang'].iloc[i] * -1,
                     s=str_thay_doi_xep_hang,
                     color= mau_thay_doi_xep_hang, va="center", ha="right", fontsize= size_pci,
                     fontweight="bold", stretch='ultra-condensed', alpha=0.7)


        if khac_nam_2006:
            diem_ket_line_mo_2 = max(toa_do_x_pci_khoi_dau, toa_do_x_pci_hien_tai) + 4.5
            diem_ket_line_mo_2 = diem_ket_line_mo_2 if diem_ket_line_mo_2 < (xmax + 2) else (xmax + 2)
            plt.hlines(y=data['xep_hang_bien_chay'].iloc[i],
                        xmin= (xmax), xmax=diem_ket_line_mo_2,
                        linewidths=0.3, linestyles='dotted', color=mau_line, alpha=0.45)

            # Ghi chú thay đổi thứ hạng
            str_ghi_chu_thu_hang = 'THỨ HẠNG ' + str(data['nam'].iloc[0])  + '\nSO VỚI 2006'
            plt.text(x=xmax + 3, y= 0.5,
                     s= str_ghi_chu_thu_hang,
                     color= mau_tieu_de, va="center", ha="right", fontsize= size_pci,
                     stretch='ultra-condensed', alpha=0.5)

    # Tạo chữ ký
    plt.text(xmax + 2, -65,
             'Thể hiện: Võ Văn Thương\nNguồn dữ liệu: http://pcivietnam.org',
             color= mau_tieu_de, va="center", ha="right", fontsize = 5)

    plt.axis('off')
    fig.canvas.draw()
    image_from_plot = fig.canvas.tostring_rgb()
    image_from_plot = np.frombuffer(image_from_plot, dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    image_from_plot = image_from_plot.reshape(h, w, 3)
    # Conver qua mảng BGR theo định dạng của OpenCV
    image_from_plot = cv2.cvtColor(image_from_plot, cv2.COLOR_RGB2BGR)
    plt.close(fig)
    return image_from_plot
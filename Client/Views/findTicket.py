import tkinter as tk
from tkinter import ttk
import socket
import json


# Hàm kết nối qua socket để gửi và nhận dữ liệu từ server
def get_all_stations():
    host = '192.168.1.20'  # Địa chỉ host của server
    port = 27047  # Port của server

    request_data = json.dumps({"action": "get_all_routes"})  # Dữ liệu gửi đi (JSON)
    buffer_size = 4096  # Kích thước bộ đệm nhận dữ liệu

    try:
        # Tạo socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))  # Kết nối tới server

            # Gửi dữ liệu
            s.sendall(request_data.encode('utf-8'))

            # Nhận phản hồi
            response_data = b""
            while True:
                part = s.recv(buffer_size)
                if not part:
                    break
                response_data += part

            # Giải mã dữ liệu nhận được từ server
            stations = json.loads(response_data.decode('utf-8'))
            print(f"Nhan duoc data: {stations}")
            return stations
    except socket.error as e:
        print(f"Lỗi khi kết nối đến server: {e}")
        return None


# Hàm tìm kiếm chuyến tàu
def search_trains(tuyen, huong, ngay_di):
    host = '192.168.1.20'
    port = 27047
    request_data = json.dumps({
        "action": "search_trains",
        "data": {
            "TuyenID": tuyen,  # Đã đổi tên biến để phản ánh sự thay đổi
            "Huong": huong,  # Đã đổi tên biến để phản ánh sự thay đổi
            "NgayKhoiHanh": ngay_di
        }
    })
    buffer_size = 4096

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))  # Kết nối tới server

            # Gửi yêu cầu
            s.sendall(request_data.encode('utf-8'))

            # Nhận phản hồi
            response_data = b""
            while True:
                part = s.recv(buffer_size)
                if not part:
                    break
                response_data += part

            # Giải mã dữ liệu nhận được từ server
            trains_data = json.loads(response_data.decode('utf-8'))
            return trains_data
    except socket.error as e:
        print(f"Lỗi khi kết nối đến server: {e}")
        return None


# Điền dữ liệu vào các combobox
def populate_comboboxes():
    stations_data = get_all_stations()

    if stations_data is None:
        print("Lỗi khi lấy dữ liệu từ máy chủ.")
        return

    tuyen_list = []
    huong_list = []

    # Lấy dữ liệu chỉ gồm GaID và Ten, hiển thị Ten
    for station in stations_data.get('data', []):
        tuyen_list.append(station['Ten'])  # Chỉ lấy 'Ten'
        huong_list.append(station['Ten'])  # Chỉ lấy 'Ten'

    # Điền dữ liệu vào các combobox
    combobox_tuyen['values'] = tuyen_list
    combobox_huong['values'] = huong_list


# Hàm gọi khi nhấn nút tìm kiếm
def tim_kiem():
    tuyen = combobox_tuyen.get()  # Lấy giá trị từ combobox 'Tên tuyến'
    huong = combobox_huong.get()  # Lấy giá trị từ combobox 'Hướng'
    ngay_khoi_hanh = entry_date.get()  # Lấy giá trị từ input 'Ngày khởi hành'

    # Gọi hàm search_trains để gửi dữ liệu tới server
    trains_data = search_trains(tuyen, huong, ngay_khoi_hanh)

    if trains_data is None:
        result_text = "Lỗi khi tìm kiếm chuyến tàu."
    elif trains_data.get('status') == 'success':
        found_route = False
        result_text = f"Tuyến tàu từ {tuyen} đến {huong} khởi hành vào {ngay_khoi_hanh}:\n"

        for train in trains_data.get('data', []):
            found_route = True
            result_text += f"- Tàu {train['ten_tau']}, giờ khởi hành: {train['gio_khoi_hanh']}\n"

        if not found_route:
            result_text = f"Không tìm thấy chuyến tàu từ {tuyen} đến {huong} vào ngày {ngay_khoi_hanh}."
    else:
        result_text = "Không tìm thấy chuyến tàu phù hợp."

    label_ket_qua.config(text=result_text)


# Tạo cửa sổ chính
root = tk.Tk()
root.title("Metroway Dashboard")
root.geometry("800x500")
root.configure(bg="white")  # Set background to white

# Title Label
title_label = tk.Label(root, text="Dashboard", font=("Arial", 20), bg="white", fg="blue")
title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=20, sticky="w")

# Input fields for 'Tên tuyến', 'Hướng', and 'Ngày khởi hành'
input_frame = tk.Frame(root, bg="white")
input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")

label_tuyen = tk.Label(input_frame, text="Tên tuyến", font=("Arial", 12), bg="white")
label_tuyen.grid(row=0, column=0, padx=10)
combobox_tuyen = ttk.Combobox(input_frame, width=15)
combobox_tuyen.grid(row=0, column=1, padx=10)

label_huong = tk.Label(input_frame, text="Hướng", font=("Arial", 12), bg="white")
label_huong.grid(row=0, column=2, padx=10)
combobox_huong = ttk.Combobox(input_frame, width=15)
combobox_huong.grid(row=0, column=3, padx=10)

label_date = tk.Label(input_frame, text="Ngày khởi hành", font=("Arial", 12), bg="white")
label_date.grid(row=0, column=4, padx=10)
entry_date = tk.Entry(input_frame, width=15)
entry_date.grid(row=0, column=5, padx=10)

# Search button
search_button = tk.Button(root, text="Tìm kiếm", width=20, bg="blue", fg="white", font=("Arial", 12), command=tim_kiem)
search_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")

# Populate comboboxes with station data
populate_comboboxes()

# Results section
results_label = tk.Label(root, text="Kết quả", font=("Arial", 14), bg="white")
results_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

# Result placeholders
result_frame = tk.Frame(root, bg="white")
result_frame.grid(row=4, column=0, padx=20, sticky="w")

label_ket_qua = tk.Label(result_frame, text="", width=60, height=2, bg="#f0f0f0", relief="solid", anchor="w",
                         justify="left")
label_ket_qua.grid(row=0, column=0, pady=5)

# Side menu for 'Đặt vé', 'Danh sách vé đã đặt', and 'Thống kê'
side_frame = tk.Frame(root, bg="white")
side_frame.grid(row=1, column=1, rowspan=2, padx=30, pady=10, sticky="n")

side_label1 = tk.Label(side_frame, text="Đặt vé", font=("Arial", 12), bg="white")
side_label1.pack(pady=10)
side_label2 = tk.Label(side_frame, text="Danh sách vé đã đặt", font=("Arial", 12), bg="white")
side_label2.pack(pady=10)
side_label3 = tk.Label(side_frame, text="Thống kê", font=("Arial", 12), bg="white")
side_label3.pack(pady=10)

# Notifications area
notif_frame = tk.Frame(root, bg="white")
notif_frame.grid(row=3, column=1, padx=30, pady=10, sticky="n")

notif_label = tk.Label(notif_frame, text="Thông báo", font=("Arial", 12), bg="white")
notif_label.pack(pady=10)

# Start the main loop
root.mainloop()
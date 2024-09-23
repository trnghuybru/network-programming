import tkinter as tk
from tkinter import ttk
import socket
import json
import subprocess  # Để chạy bookticket.py


# Hàm kết nối qua socket để gửi và nhận dữ liệu từ server
def get_all_stations():
    host = '172.20.10.3'  # Địa chỉ host của server
    port = 27049  # Port của server

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
            return stations
    except socket.error as e:
        print(f"Lỗi khi kết nối đến server: {e}")
        return None


# Hàm tìm kiếm chuyến tàu
def search_trains(tuyen, huong, ngay_di):
    host = '172.20.10.3'
    port = 27049
    request_data = json.dumps({
        "action": "search_trains",
        "data": {
            "TuyenID": tuyen,
            "Huong": huong,
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
            print(f"Cac tau kha dung: {trains_data}")
            return trains_data
    except socket.error as e:
        print(f"Lỗi khi kết nối đến server: {e}")
        return None


# Hàm gửi yêu cầu lấy thông tin toa tàu
# Hàm gửi yêu cầu lấy thông tin toa tàu
def print_carriages(tau_id):
    host = '172.20.10.3'
    port = 27049
    request_data = json.dumps({
        "action": "print_carriages",
        "data": {
            "tau_id": tau_id
        }
    })
    print(f"Request print_carriages: {request_data}")  # In request

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(request_data.encode('utf-8'))

            response_data = b""
            while True:
                part = s.recv(4096)
                if not part:
                    break
                response_data += part

            response = response_data.decode('utf-8')
            print(f"Response from server: {response}")  # In toàn bộ phản hồi từ server
            carriages_data = json.loads(response)
            return carriages_data
    except socket.error as e:
        print(f"Lỗi khi kết nối đến server: {e}")
        return None




# Điền dữ liệu vào các combobox
def populate_comboboxes():
    stations_data = get_all_stations()

    if stations_data is None:
        print("Lỗi khi lấy dữ liệu từ máy chủ.")
        return

    tuyen_dict = {}
    huong_list = []

    for station in stations_data.get('data', []):
        tuyen_dict[station['Ten']] = station['TuyenID']
        huong_list.append(station['Ten'])

    combobox_tuyen['values'] = list(tuyen_dict.keys())
    combobox_huong['values'] = huong_list

    return tuyen_dict


# Hàm gọi khi nhấn nút tìm kiếm
# Hiển thị thông tin chuyến tàu và tạo nút Đặt vé
def tim_kiem():
    tuyen = combobox_tuyen.get()
    huong = combobox_huong.get()
    ngay_khoi_hanh = entry_date.get()

    tuyen_dict = populate_comboboxes()
    tuyen_id = tuyen_dict.get(tuyen)

    if not tuyen_id:
        label_ket_qua.config(text="Không tìm thấy TuyenID cho tên tuyến này.")
        return

    trains_data = search_trains(tuyen_id, huong, ngay_khoi_hanh)

    if trains_data is None:
        label_ket_qua.config(text="Lỗi khi tìm kiếm chuyến tàu.")
    elif trains_data.get('status') == 'success':
        label_ket_qua.config(text="Tìm thấy các chuyến tàu phù hợp.")

        # Xóa các kết quả cũ trước khi hiển thị kết quả mới
        for widget in result_frame.winfo_children():
            widget.destroy()

        row_index = 0
        for train in trains_data.get('data', []):
            # Hiển thị thông tin chuyến tàu
            train_info = f"Tàu {train['TenTau']}, giờ khởi hành: {train['GioDi']}"
            label_train_info = tk.Label(result_frame, text=train_info, width=40, bg="#f0f0f0", anchor="w",
                                        justify="left")
            label_train_info.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")

            # Tạo nút Đặt vé và truyền tên tuyến cùng ID của tàu
            button_dat_ve = tk.Button(result_frame, text="Đặt vé", width=10, bg="green", fg="white",
                                      command=lambda tau_id=train['TauID']: dat_ve(combobox_tuyen.get(), tau_id))
            button_dat_ve.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")

            row_index += 1

    else:
        label_ket_qua.config(text="Không tìm thấy chuyến tàu phù hợp.")





# Hàm mở form Đặt vé
# Hàm gọi khi nhấn nút Đặt vé
def dat_ve(ten_tuyen, tau_id):
    print(f"Đặt vé cho tuyến {ten_tuyen}, tàu {tau_id}")

    # Gửi yêu cầu lấy thông tin toa tàu
    carriages_data = print_carriages(tau_id)

    if carriages_data is None or carriages_data.get('status') != 'success':
        print(f"Toa tàu: {carriages_data}")
        print("Lỗi khi lấy thông tin toa tàu.")
        return

    # Truyền danh sách tên toa (giả sử server trả về danh sách các toa)
    ds_toa = ",".join([toa['TenToa'] for toa in carriages_data.get('data', [])])
    subprocess.Popen(['python3', 'seat.py', ten_tuyen, ds_toa])


# Tạo cửa sổ chính
root = tk.Tk()
root.title("Metroway Dashboard")
root.geometry("800x500")
root.configure(bg="white")

# Title Label
title_label = tk.Label(root, text="Dashboard", font=("Arial", 20), bg="white", fg="blue")
title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=20, sticky="w")

# Input fields
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

# Label for search result status
label_ket_qua = tk.Label(root, text="", font=("Arial", 12), bg="white", fg="red")
label_ket_qua.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Result placeholders
result_frame = tk.Frame(root, bg="white")
result_frame.grid(row=4, column=0, padx=20, pady=10, sticky="w")

# Start the main loop
root.mainloop()
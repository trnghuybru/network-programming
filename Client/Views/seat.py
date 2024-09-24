import tkinter as tk
from tkinter import ttk, messagebox
import sys
import socket
import json
import subprocess

# Lấy tham số từ dòng lệnh
ten_tuyen = sys.argv[1] if len(sys.argv) > 1 else "Không rõ tuyến"
ds_toa = sys.argv[2].split(',') if len(sys.argv) > 2 else ["Toa 1", "Toa 2", "Toa 3"]
tau_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1  # Lấy tau_id từ tham số thứ ba

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chọn ghế")
root.geometry("500x680")

# Hiển thị tên tuyến
route_label = tk.Label(root, text=f"Chọn chỗ cho tuyến: {ten_tuyen}", font=("Arial", 16))
route_label.pack(pady=10)

# Tạo khung cho phần chọn toa
toa_frame = tk.Frame(root)
toa_frame.pack(pady=10)

# Dropdown (Combobox) để chọn tên toa
toa_label = tk.Label(toa_frame, text="Chọn Toa:", font=("Arial", 14))
toa_label.pack(side=tk.LEFT)

combobox_toa = ttk.Combobox(toa_frame, values=ds_toa)
combobox_toa.pack(side=tk.LEFT, padx=5)
combobox_toa.set(ds_toa[0])  # Set toa mặc định là toa đầu tiên trong danh sách

# Ngày khởi hành
ngay_khoi_hanh = "2024-08-20"

# Màu sắc tương ứng cho các trạng thái ghế
seat_colors = {0: "blue", 1: "red", 2: "yellow"}

# Hàm lấy danh sách ghế từ server
def get_seat_status(toa_id):
    HOST = '172.20.10.3'  # Địa chỉ server
    PORT = 27049  # Cổng server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        payload = {
            "action": "get_seats_in_carriage",
            "data": {
                "toa_id": toa_id,
                "ngay_khoi_hanh": ngay_khoi_hanh
            }
        }
        s.sendall(json.dumps(payload).encode('utf-8'))
        response = s.recv(4096)
        print(f"Lay gheeeee: {json.loads(response.decode('utf-8'))}")
        return json.loads(response.decode('utf-8'))

# Biến toàn cục chứa trạng thái các ghế
seat_status = {}

# Khởi tạo danh sách ghế
def initialize_seat_status():
    global seat_status
    toa_id = combobox_toa.current() + 1  # Giả sử ID toa là vị trí trong danh sách + 1
    response = get_seat_status(toa_id)

    if response.get("status") == "success":
        # Lưu cả GheID và SoGhe trong seat_status
        seat_status = {seat["GheID"]: {"SoGhe": seat["SoGhe"], "TrangThai": seat["TrangThai"]} for seat in response["data"]}
    else:
        messagebox.showerror("Lỗi", "Không thể lấy thông tin ghế.")

    # Đảm bảo rằng trạng thái ghế nằm trong những giá trị cho phép
    for seat in seat_status:
        if seat_status[seat]["TrangThai"] not in seat_colors:
            seat_status[seat]["TrangThai"] = 0  # Đặt lại về trạng thái trống nếu không hợp lệ

# Tạo khung chứa ghế
seat_frame = tk.Frame(root)
seat_frame.pack(pady=20)

# Danh sách ghế đã chọn
selected_seats = []

# Hàm khi chọn ghế
def select_seat(ghe_id):
    if ghe_id not in buttons:
        messagebox.showerror("Lỗi", f"Ghế {seat_status[ghe_id]['SoGhe']} không tồn tại.")
        return

    if seat_status[ghe_id]["TrangThai"] == 0:  # Nếu ghế trống
        seat_status[ghe_id]["TrangThai"] = 2  # Đánh dấu là ghế đang chọn
        buttons[ghe_id].config(bg=seat_colors[2])  # Đổi màu ghế thành vàng
        selected_seats.append(ghe_id)  # Thêm ghế đã chọn vào danh sách
    elif seat_status[ghe_id]["TrangThai"] == 2:  # Nếu ghế đã chọn, bỏ chọn
        seat_status[ghe_id]["TrangThai"] = 0  # Đặt lại ghế thành trạng thái trống
        buttons[ghe_id].config(bg=seat_colors[0])  # Đổi màu ghế thành xanh
        selected_seats.remove(ghe_id)  # Xóa ghế khỏi danh sách
    elif seat_status[ghe_id]["TrangThai"] == 1:  # Nếu ghế đã đặt
        messagebox.showinfo("Thông báo", "Ghế này đã được đặt.")

# Khởi tạo danh sách ghế
initialize_seat_status()

# Tạo khung chứa các dãy ghế bên trái và bên phải với khoảng trống lớn ở giữa
left_frame = tk.Frame(seat_frame)
left_frame.grid(row=0, column=0, padx=20, pady=10)  # Dãy ghế bên trái

right_frame = tk.Frame(seat_frame)
right_frame.grid(row=0, column=2, padx=20, pady=10)  # Dãy ghế bên phải

# Tạo nút cho từng ghế
buttons = {}
row_left = 0
row_right = 0

for ghe_id, info in seat_status.items():
    so_ghe = info["SoGhe"]
    status = info["TrangThai"]
    if so_ghe <= 12:  # Ghế từ 1 đến 12 nằm bên trái
        btn = tk.Button(left_frame, text=f"{so_ghe}", width=5, height=2,
                        bg=seat_colors[status], fg="white",
                        font=("Arial", 10, "bold"),
                        command=lambda ghe_id=ghe_id: select_seat(ghe_id))
        btn.grid(row=row_left // 2, column=row_left % 2, padx=5, pady=5)
        buttons[ghe_id] = btn  # Thêm nút vào dictionary buttons
        row_left += 1
    else:  # Ghế từ 13 đến 24 nằm bên phải
        btn = tk.Button(right_frame, text=f"{so_ghe}", width=5, height=2,
                        bg=seat_colors[status], fg="white",
                        font=("Arial", 10, "bold"),
                        command=lambda ghe_id=ghe_id: select_seat(ghe_id))
        btn.grid(row=row_right // 2, column=row_right % 2, padx=5, pady=5)
        buttons[ghe_id] = btn  # Thêm nút vào dictionary buttons
        row_right += 1

# Hàm lấy ga đi và ga đến
def get_start_and_destination_stations(tau_id):
    HOST = '172.20.10.3'  # Địa chỉ server
    PORT = 27049  # Cổng server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        payload = {
            "action": "get_start_and_destination_stations",
            "data": {
                "tau_id": tau_id
            }
        }
        s.sendall(json.dumps(payload).encode('utf-8'))
        response = s.recv(4096)
        print(json.loads(response.decode('utf-8')))
        return json.loads(response.decode('utf-8'))


# Hàm gửi yêu cầu lấy giá ghế
def get_price():
    response = get_start_and_destination_stations(tau_id)  # Lấy ga đi và ga đến

    # Kiểm tra xem phản hồi có 'data' không
    if "data" not in response:
        messagebox.showerror("Lỗi", "Không thể lấy ga đi và ga đến.")
        return {"status": "error"}

    # Kiểm tra xem data có phải là danh sách không
    if isinstance(response["data"], list) and len(response["data"]) > 0:
        # Lấy ga đi và ga đến từ phần tử đầu tiên
        ga_data = response["data"][0]  # Lấy phần tử đầu tiên
        ga_di_id = ga_data.get("GaDiID")  # Sử dụng khóa đúng
        ga_den_id = ga_data.get("GaDenID")  # Sử dụng khóa đúng

        if ga_di_id is None or ga_den_id is None:
            messagebox.showerror("Lỗi", "Không thể lấy ga đi và ga đến.")
            return {"status": "error"}
    else:
        messagebox.showerror("Lỗi", "Không thể lấy ga đi và ga đến.")
        return {"status": "error"}

    ghe_id = selected_seats[0] if selected_seats else None  # Lấy ghế đầu tiên đã chọn

    # Tạo payload để gửi đến server
    payload = {
        "action": "get_price",
        "data": {
            "tau_id": tau_id,
            "ga_di_id": ga_di_id,
            "ga_den_id": ga_den_id,
            "ghe_id": ghe_id
        }
    }
    HOST = '172.20.10.3'  # Địa chỉ server
    PORT = 27049  # Cổng server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(payload).encode('utf-8'))
        response = s.recv(4096)
        print(f"gia: {json.loads(response.decode('utf-8'))}")
        return json.loads(response.decode('utf-8'))



# Hàm chuyển sang màn hình xác nhận
def show_confirmation():
    if not selected_seats:
        messagebox.showwarning("Cảnh báo", "Bạn chưa chọn ghế nào!")
        return

    confirm_window = tk.Toplevel(root)
    confirm_window.title("Xác nhận ghế")
    confirm_window.geometry("300x300")

    tk.Label(confirm_window, text="Thông tin xác nhận:", font=("Arial", 14)).pack(pady=10)

    # Hiển thị thông tin
    tk.Label(confirm_window, text=f"Tàu ID: {tau_id}", font=("Arial", 12)).pack()
    tk.Label(confirm_window, text=f"Ghế ID: {selected_seats[0]}", font=("Arial", 12)).pack()
    tk.Label(confirm_window, text=f"Ngày khởi hành: {ngay_khoi_hanh}", font=("Arial", 12)).pack()

    # Lấy giá ghế
    price_response = get_price()
    if price_response.get("status") == "success":
        # Sử dụng khóa đúng để lấy giá
        price = price_response["data"].get("gia_tien")  # Thay 'price' bằng 'gia_tien'
        tk.Label(confirm_window, text=f"Giá ghế: {str(price)} VNĐ", font=("Arial", 12)).pack()
    else:
        tk.Label(confirm_window, text="Không thể lấy giá ghế.", font=("Arial", 12)).pack()

    # Nút xác nhận
    tk.Button(confirm_window, text="Xác nhận", command=lambda: confirm_selection(confirm_window)).pack(pady=10)

# Hàm gửi yêu cầu khóa ghế
def lock_seat(ghe_id):
    payload = {
        "action": "seat_locking",
        "data": {
            "tau_id": tau_id,
            "ghe_id": ghe_id,
            "ngay_khoi_hanh": ngay_khoi_hanh
        }
    }

    HOST = '172.20.10.3'  # Địa chỉ server
    PORT = 27049  # Cổng server
    print(f"Lock ghe: {payload}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(payload).encode('utf-8'))
        response = s.recv(4096)
        print(f"Lock ghe server tra ve: {json.loads(response.decode('utf-8'))}")
        return json.loads(response.decode('utf-8'))


# Hàm xử lý xác nhận và chuyển sang file bookTicket.py
def confirm_selection(confirm_window):
    ghe_id = selected_seats[0] if selected_seats else None
    if ghe_id is not None:
        lock_response = lock_seat(ghe_id)  # Gửi yêu cầu khóa ghế
        if lock_response.get("status") == "success":
            messagebox.showinfo("Thông báo", "Ghế đã được khóa thành công!")

            # Lấy ga đi và ga đến
            ga_info = get_start_and_destination_stations(tau_id)
            ga_di_id = ga_info["data"][0]["GaDiID"] if "data" in ga_info and len(ga_info["data"]) > 0 else None
            ga_den_id = ga_info["data"][0]["GaDenID"] if "data" in ga_info and len(ga_info["data"]) > 0 else None

            # Lấy giá vé
            price_response = get_price()
            price = price_response["data"].get("gia_tien") if price_response.get("status") == "success" else "Không rõ"

            # Chạy file bookticket.py với các tham số cần thiết, bao gồm cả giá vé
            subprocess.run(
                ['python3', 'network-programming/Client/Views/bookticket.py', str(ten_tuyen), str(tau_id), str(ga_di_id), str(ga_den_id), ngay_khoi_hanh,
                 str(ghe_id), str(price)])
        else:
            messagebox.showerror("Lỗi", "Không thể khóa ghế. Vui lòng thử lại.")
    confirm_window.destroy()  # Đóng cửa sổ xác nhận


# Nút Xác nhận ghế
confirm_button = tk.Button(root, text="Xác nhận ghế", width=20, height=2, bg="green", fg="white",
                           command=show_confirmation)
confirm_button.pack(pady=20)

root.mainloop()
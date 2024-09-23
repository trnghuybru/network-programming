import tkinter as tk
from tkinter import ttk, messagebox
import sys
import socket
import json


# Lấy tham số từ dòng lệnh
ten_tuyen = sys.argv[1] if len(sys.argv) > 1 else "Không rõ tuyến"
ds_toa = sys.argv[2].split(',') if len(sys.argv) > 2 else ["Toa 1", "Toa 2", "Toa 3"]


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


# Ngày khởi hành (có thể thay đổi theo yêu cầu)
ngay_khoi_hanh = "2024-08-20"


# Màu sắc tương ứng cho các trạng thái ghế
seat_colors = {0: "blue", 1: "red", 2: "yellow"}


# Hàm lấy danh sách ghế từ server
def get_seat_status(toa_id):
   # Kết nối đến server
   HOST = '172.20.10.3'  # Địa chỉ server
   PORT = 27049  # Cổng server


   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
       s.connect((HOST, PORT))


       # Tạo payload
       payload = {
           "action": "get_seats_in_carriage",
           "data": {
               "toa_id": toa_id,
               "ngay_khoi_hanh": ngay_khoi_hanh
           }
       }
       s.sendall(json.dumps(payload).encode('utf-8'))


       # Nhận phản hồi từ server
       response = s.recv(4096)
       return json.loads(response.decode('utf-8'))


# Biến toàn cục chứa trạng thái các ghế
seat_status = {}


# Khởi tạo danh sách ghế
def initialize_seat_status():
   global seat_status  # Đảm bảo sử dụng biến toàn cục
   toa_id = combobox_toa.current() + 1  # Giả sử ID toa là vị trí trong danh sách + 1
   response = get_seat_status(toa_id)


   if response.get("status") == "success":
       # Tạo danh sách ghế dựa vào response
       seat_status = {seat["SoGhe"]: seat["TrangThai"] for seat in response["data"]}  # Lưu trạng thái của từng ghế
   else:
       messagebox.showerror("Lỗi", "Không thể lấy thông tin ghế.")


# Tạo khung chứa ghế
seat_frame = tk.Frame(root)
seat_frame.pack(pady=20)


# Danh sách ghế đã chọn
selected_seats = []


# Hàm khi chọn ghế
def select_seat(so_ghe):
   if seat_status[so_ghe] == 0:  # Nếu ghế trống
       seat_status[so_ghe] = 2  # Đánh dấu là ghế đang chọn
       buttons[so_ghe].config(bg=seat_colors[2])  # Đổi màu ghế thành vàng
       selected_seats.append(so_ghe)  # Thêm ghế đã chọn vào danh sách
   elif seat_status[so_ghe] == 2:  # Nếu ghế đã chọn, bỏ chọn
       seat_status[so_ghe] = 0  # Đặt lại ghế thành trạng thái trống
       buttons[so_ghe].config(bg=seat_colors[0])  # Đổi màu ghế thành xanh
       selected_seats.remove(so_ghe)  # Xóa ghế khỏi danh sách
   elif seat_status[so_ghe] == 1:  # Nếu ghế đã đặt
       messagebox.showinfo("Thông báo", "Ghế này đã được đặt.")


# Khởi tạo danh sách ghế
initialize_seat_status()


# Tạo khung chứa các dãy ghế bên trái và bên phải với khoảng trống lớn ở giữa
left_frame = tk.Frame(seat_frame)
left_frame.grid(row=0, column=0, padx=20, pady=10)  # Dãy ghế bên trái


right_frame = tk.Frame(seat_frame)
right_frame.grid(row=0, column=2, padx=20, pady=10)  # Dãy ghế bên phải


# Tạo nút cho từng ghế (chia thành 2 dãy với lối đi ở giữa)
buttons = {}
row_left = 0
row_right = 0


for seat, status in seat_status.items():
   if seat <= 12:  # Ghế từ 1 đến 12 nằm bên trái
       btn = tk.Button(left_frame, text=f"{seat}", width=5, height=2,
                       bg=seat_colors[status], fg="white",  # Màu chữ trắng
                       font=("Arial", 10, "bold"),  # In đậm số ghế
                       command=lambda seat=seat: select_seat(seat))
       btn.grid(row=row_left // 2, column=row_left % 2, padx=5, pady=5)
       row_left += 1


   else:  # Ghế từ 13 đến 24 nằm bên phải
       btn = tk.Button(right_frame, text=f"{seat}", width=5, height=2,
                       bg=seat_colors[status], fg="white",  # Màu chữ trắng
                       font=("Arial", 10, "bold"),  # In đậm số ghế
                       command=lambda seat=seat: select_seat(seat))
       btn.grid(row=row_right // 2, column=row_right % 2, padx=5, pady=5)
       row_right += 1

# Hàm chuyển sang màn hình xác nhận
def show_confirmation():
   if not selected_seats:
       messagebox.showwarning("Cảnh báo", "Bạn chưa chọn ghế nào!")
       return


   confirm_window = tk.Toplevel(root)
   confirm_window.title("Xác nhận ghế")
   confirm_window.geometry("300x200")


   tk.Label(confirm_window, text="Ghế bạn đã chọn:", font=("Arial", 14)).pack(pady=10)


   for seat in selected_seats:
       tk.Label(confirm_window, text=f"Ghế {seat}", font=("Arial", 12)).pack()


   tk.Button(confirm_window, text="Xác nhận",
             command=lambda: messagebox.showinfo("Thông báo", "Đặt vé thành công!")).pack(pady=10)


# Nút Xác nhận ghế
confirm_button = tk.Button(root, text="Xác nhận ghế", width=20, height=2, bg="green", fg="white",
                          command=show_confirmation)
confirm_button.pack(pady=20)


root.mainloop()


import tkinter as tk
from tkinter import messagebox

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chọn ghế")
root.geometry("400x600")

# Tên tuyến (lấy từ màn hình trước)
TenTuyen = "Hà Nội - Hải Phòng"  # Giả sử đây là dữ liệu từ màn hình trước

# Hiển thị tên tuyến (nằm phía trên)
route_label = tk.Label(root, text=f"Chọn chỗ chiều đi: {TenTuyen}", font=("Arial", 16))
route_label.pack(pady=10)

# Hiển thị tên toa (lấy từ dữ liệu server, cũng nằm phía trên)
ten_toa = "Toa 1"  # Giả sử đây là dữ liệu từ server gửi về
train_car_label = tk.Label(root, text=f"Tên toa: {ten_toa}", font=("Arial", 14))
train_car_label.pack(pady=10)

# Khởi tạo danh sách ghế với trạng thái
# 0 = Ghế trống (xanh), 1 = Ghế đã chọn (vàng), 2 = Ghế đã bán (đỏ)
seat_status = [
    [0, 0, 1, 0],  # Hàng 1
    [0, 0, 0, 0],  # Hàng 2
    [0, 2, 0, 0],  # Hàng 3
    [0, 0, 0, 0],  # Hàng 4
    [0, 0, 0, 0],  # Hàng 5
    [0, 0, 0, 0],  # Hàng 6
]

# Màu sắc tương ứng cho các trạng thái ghế
seat_colors = {0: "blue", 1: "yellow", 2: "red"}

# Tạo khung chứa ghế
seat_frame = tk.Frame(root)
seat_frame.pack(pady=20)

# Danh sách ghế đã chọn
selected_seats = []

# Hàm khi chọn ghế
def select_seat(row, col):
    if seat_status[row][col] == 0:  # Nếu ghế trống
        seat_status[row][col] = 1  # Đánh dấu là ghế đang chọn
        buttons[row][col].config(bg=seat_colors[1])
        selected_seats.append((row, col))  # Thêm ghế đã chọn vào danh sách
    elif seat_status[row][col] == 1:  # Nếu ghế đã chọn, bỏ chọn
        seat_status[row][col] = 0
        buttons[row][col].config(bg=seat_colors[0])
        selected_seats.remove((row, col))  # Xóa ghế khỏi danh sách
    elif seat_status[row][col] == 2:  # Nếu ghế đã bán
        messagebox.showinfo("Thông báo", "Ghế này đã được bán.")

# Tạo nút cho từng ghế và chia thành hai cột
buttons = []
for r in range(len(seat_status)):
    row_buttons = []

    # Bên trái
    for c in range(2):
        btn = tk.Button(seat_frame, text=f"{r * 4 + c + 1}", width=5, height=2,
                        bg=seat_colors[seat_status[r][c]],
                        command=lambda r=r, c=c: select_seat(r, c))
        btn.grid(row=r, column=c, padx=5, pady=5)
        row_buttons.append(btn)

    # Khoảng trống giữa hai bên
    spacer = tk.Label(seat_frame, text="", width=3)
    spacer.grid(row=r, column=2)

    # Bên phải
    for c in range(2, 4):
        btn = tk.Button(seat_frame, text=f"{r * 4 + c + 1}", width=5, height=2,
                        bg=seat_colors[seat_status[r][c]],
                        command=lambda r=r, c=c: select_seat(r, c))
        btn.grid(row=r, column=c + 1, padx=5, pady=5)
        row_buttons.append(btn)

    buttons.append(row_buttons)

# Hàm chuyển sang màn hình xác nhận
def show_confirmation():
    # Kiểm tra nếu không có ghế nào được chọn
    if not selected_seats:
        messagebox.showwarning("Cảnh báo", "Bạn chưa chọn ghế nào!")
        return

    # Tạo cửa sổ xác nhận
    confirm_window = tk.Toplevel(root)
    confirm_window.title("Xác nhận ghế")
    confirm_window.geometry("300x200")

    tk.Label(confirm_window, text="Ghế bạn đã chọn:", font=("Arial", 14)).pack(pady=10)

    # Hiển thị danh sách ghế đã chọn
    for seat in selected_seats:
        seat_number = seat[0] * 4 + seat[1] + 1  # Tính số ghế
        tk.Label(confirm_window, text=f"Ghế {seat_number}", font=("Arial", 12)).pack()

    # Thêm nút Xác nhận
    tk.Button(confirm_window, text="Xác nhận",
              command=lambda: messagebox.showinfo("Thông báo", "Đặt vé thành công!")).pack(pady=10)

# Nút Xác nhận ghế
confirm_button = tk.Button(root, text="Xác nhận ghế", width=20, height=2, bg="green", fg="white",
                           command=show_confirmation)
confirm_button.pack(pady=20)

root.mainloop()

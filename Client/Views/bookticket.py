import tkinter as tk
from tkinter import messagebox
import sys
import socket
import json

# Lấy các tham số truyền vào từ dòng lệnh
ten_tuyen = sys.argv[1] if len(sys.argv) > 1 else "Không rõ tuyến"
tau_id = sys.argv[2] if len(sys.argv) > 2 else "1"
ga_di_id = sys.argv[3] if len(sys.argv) > 3 else "Không rõ Ga đi"
ga_den_id = sys.argv[4] if len(sys.argv) > 4 else "Không rõ Ga đến"
ngay_khoi_hanh = sys.argv[5] if len(sys.argv) > 5 else "Không rõ ngày"
ghe_id = sys.argv[6] if len(sys.argv) > 6 else "Không rõ ghế"
gia_ve = sys.argv[7] if len(sys.argv) > 7 else "0.0"  # Giá vé

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Đặt vé tàu")
root.geometry("500x700")

# Hiển thị thông tin đã được truyền qua
tk.Label(root, text="Thông tin đặt vé", font=("Arial", 16)).pack(pady=10)

tk.Label(root, text=f"Tuyến: {ten_tuyen}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Tàu ID: {tau_id}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Ga đi ID: {ga_di_id}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Ga đến ID: {ga_den_id}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Ngày khởi hành: {ngay_khoi_hanh}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Ghế ID: {ghe_id}", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text=f"Giá vé: {gia_ve} VND", font=("Arial", 12)).pack(pady=5)

# Tạo các ô nhập thông tin người dùng
tk.Label(root, text="Tên khách hàng:", font=("Arial", 12)).pack(pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.pack(pady=5)

tk.Label(root, text="Địa chỉ:", font=("Arial", 12)).pack(pady=5)
entry_address = tk.Entry(root, width=30)
entry_address.pack(pady=5)

tk.Label(root, text="Số điện thoại:", font=("Arial", 12)).pack(pady=5)
entry_phone = tk.Entry(root, width=30)
entry_phone.pack(pady=5)

tk.Label(root, text="Nhân viên ID:", font=("Arial", 12)).pack(pady=5)
entry_staff_id = tk.Entry(root, width=30)
entry_staff_id.pack(pady=5)

# Hàm gửi yêu cầu đặt vé tới server
def send_booking_request(booking_data):
    HOST = '172.20.10.3'
    PORT = 27049

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(booking_data).encode('utf-8'))
            response = s.recv(4096)
            return json.loads(response.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Hàm xử lý khi nhấn nút "Xác nhận"
def confirm_ticket():
    customer_name = entry_name.get()
    address = entry_address.get()
    phone = entry_phone.get()
    staff_id = entry_staff_id.get()

    if not customer_name or not address or not phone or not staff_id:
        messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin.")
        return

    # Tạo dữ liệu để gửi tới server
    booking_data = {
        "action": "book_ticket",
        "data": {
            "TuyenID": 1,  # ID của tuyến, ở đây bạn có thể thay đổi hoặc lấy từ nguồn khác
            "TauID": int(tau_id),
            "GaDi": ga_di_id,
            "GaDen": ga_den_id,
            "NgayKhoiHanh": ngay_khoi_hanh,
            "TenKH": customer_name,
            "DiaChi": address,
            "SDT": phone,
            "NhanVienID": int(staff_id),
            "GheID": int(ghe_id),
            "SoTien": float(gia_ve)  # Giá vé
        }
    }

    # Gửi yêu cầu tới server
    response = send_booking_request(booking_data)

    # Xử lý phản hồi từ server
    if response.get("status") == "success":
        messagebox.showinfo("Thành công", "Đặt vé thành công!")
    else:
        error_message = response.get("message", "Không thể đặt vé. Vui lòng thử lại sau.")
        messagebox.showerror("Lỗi", error_message)

# Nút xác nhận
btn_confirm = tk.Button(root, text="Xác nhận", width=20, height=2, bg="green", fg="white", command=confirm_ticket)
btn_confirm.pack(pady=20)

# Bắt đầu vòng lặp chính
root.mainloop()

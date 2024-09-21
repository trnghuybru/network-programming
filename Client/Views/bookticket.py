import tkinter as tk
from tkinter import messagebox
import requests

# Hàm để gửi yêu cầu đặt vé
def book_ticket():
    ten_kh = entry_ten_kh.get()
    dia_chi = entry_dia_chi.get()
    sdt = entry_sdt.get()
    ghe_id = entry_ghe_id.get()
    tau_id = entry_tau_id.get()
    ga_di = entry_ga_di.get()
    ga_den = entry_ga_den.get()
    ngay_khoi_hanh = entry_ngay_khoi_hanh.get()
    nhan_vien_id = entry_nhan_vien_id.get()

    # Kiểm tra đầu vào
    if not all([ten_kh, dia_chi, sdt, ghe_id, tau_id, ga_di, ga_den, ngay_khoi_hanh, nhan_vien_id]):
        messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
        return

    # Dữ liệu để gửi lên server
    data = {
        "action": "book_ticket",
        "data": {
            "TenKH": ten_kh,
            "DiaChi": dia_chi,
            "SDT": sdt,
            "GheID": int(ghe_id),
            "TauID": int(tau_id),
            "GaDi": int(ga_di),
            "GaDen": int(ga_den),
            "NgayKhoiHanh": ngay_khoi_hanh,
            "NhanVienID": int(nhan_vien_id)
        }
    }

    try:
        # Giả lập request API (đặt đường dẫn API của bạn)
        response = requests.post("https://your-api-url.com/book_ticket", json=data)

        # Kiểm tra kết quả
        if response.status_code == 200:
            messagebox.showinfo("Thành công", "Đặt vé thành công!")
        else:
            messagebox.showerror("Thất bại", "Đặt vé thất bại.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể kết nối tới server: {e}")

# Tạo giao diện người dùng
root = tk.Tk()
root.title("Đặt vé tàu")
root.geometry("400x500")
root.configure(bg="#f0f0f0")

# Tiêu đề
title_label = tk.Label(root, text="Form Đặt Vé Tàu", font=("Arial", 20), bg="#f0f0f0", fg="blue")
title_label.pack(pady=10)

# Các trường nhập thông tin khách hàng
def add_label_entry(text, root):
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(pady=5)
    label = tk.Label(frame, text=text, font=("Arial", 12), width=15, anchor="w", bg="#f0f0f0")
    label.pack(side="left")
    entry = tk.Entry(frame, width=25)
    entry.pack(side="left")
    return entry

entry_ten_kh = add_label_entry("Tên khách hàng", root)
entry_dia_chi = add_label_entry("Địa chỉ", root)
entry_sdt = add_label_entry("Số điện thoại", root)
entry_ghe_id = add_label_entry("ID ghế", root)
entry_tau_id = add_label_entry("ID tàu", root)
entry_ga_di = add_label_entry("Ga đi (ID)", root)
entry_ga_den = add_label_entry("Ga đến (ID)", root)
entry_ngay_khoi_hanh = add_label_entry("Ngày khởi hành", root)
entry_nhan_vien_id = add_label_entry("ID nhân viên", root)

# Nút đặt vé
book_button = tk.Button(root, text="Đặt vé", font=("Arial", 12), bg="green", fg="white", command=book_ticket)
book_button.pack(pady=20)

# Chạy chương trình
root.mainloop()

import sys
import socket
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QFormLayout


class TrainBookingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Nhập thông tin đặt vé tàu')
        self.setGeometry(100, 100, 400, 300)

        # Tạo layout chính
        layout = QVBoxLayout()

        # Tạo layout cho form
        form_layout = QFormLayout()

        # Tên khách hàng
        self.customer_name_input = QLineEdit()
        form_layout.addRow(QLabel('Tên khách hàng:'), self.customer_name_input)

        # Địa chỉ
        self.address_input = QLineEdit()
        form_layout.addRow(QLabel('Địa chỉ:'), self.address_input)

        # Số điện thoại
        self.phone_input = QLineEdit()
        form_layout.addRow(QLabel('Số điện thoại:'), self.phone_input)

        # Chuyến tàu
        self.train_trip_input = QLineEdit()
        form_layout.addRow(QLabel('Chuyến tàu:'), self.train_trip_input)

        # Loại ghế
        self.seat_type_input = QLineEdit()  # Assuming this will be an ID or some other value
        form_layout.addRow(QLabel('Ghế ID:'), self.seat_type_input)

        # Ga đi
        self.station_from_input = QLineEdit()
        form_layout.addRow(QLabel('Ga đi:'), self.station_from_input)

        # Ga đến
        self.station_to_input = QLineEdit()
        form_layout.addRow(QLabel('Ga đến:'), self.station_to_input)

        # Ngày khởi hành
        self.departure_date_input = QLineEdit()
        form_layout.addRow(QLabel('Ngày khởi hành:'), self.departure_date_input)

        # Nút bấm để xác nhận
        self.submit_button = QPushButton('Xác nhận')
        self.submit_button.clicked.connect(self.submit_info)

        # Thêm form layout vào layout chính
        layout.addLayout(form_layout)
        layout.addWidget(self.submit_button)

        # Đặt layout chính cho cửa sổ
        self.setLayout(layout)

    def submit_info(self):
        # Lấy dữ liệu từ các trường
        customer_name = self.customer_name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        train_trip = self.train_trip_input.text()
        seat_type = self.seat_type_input.text()
        station_from = self.station_from_input.text()
        station_to = self.station_to_input.text()
        departure_date = self.departure_date_input.text()

        # Tạo dữ liệu dạng JSON để gửi đến server
        ticket_info = {
            'TenKH': customer_name,
            'DiaChi': address,
            'SDT': phone,
            'TauID': int(train_trip),  # Assuming TauID is an integer
            'GheID': int(seat_type),   # Assuming GheID is an integer
            'GaDi': int(station_from), # Assuming GaDi is an integer
            'GaDen': int(station_to),  # Assuming GaDen is an integer
            'NgayKhoiHanh': departure_date
        }

        # Kết nối tới server và gửi yêu cầu đặt vé
        self.send_request_to_server(ticket_info)

    def send_request_to_server(self, data):
        try:
            # Tạo socket kết nối tới server (IP: 127.0.0.1, Port: 2704)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 2704))

                # Gửi dữ liệu đến server dưới dạng JSON
                request = json.dumps({
                    'action': 'sell_ticket',
                    'data': data
                }).encode('utf-8')

                s.sendall(request)

                # Nhận phản hồi từ server
                response = s.recv(1024).decode('utf-8')
                response_data = json.loads(response)

                # In kết quả phản hồi từ server
                print(f"Phản hồi từ server: {response_data}")
        except Exception as e:
            print(f"Lỗi kết nối tới server: {e}")


# Tạo ứng dụng
app = QApplication(sys.argv)

# Tạo và hiển thị giao diện
window = TrainBookingApp()
window.show()

# Chạy ứng dụng
sys.exit(app.exec_())

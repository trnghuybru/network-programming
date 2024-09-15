import sys
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

        # Chuyến tàu
        self.train_trip_input = QLineEdit()
        form_layout.addRow(QLabel('Chuyến tàu:'), self.train_trip_input)

        # Ga tàu
        self.station_input = QLineEdit()
        form_layout.addRow(QLabel('Ga tàu:'), self.station_input)

        # Loại ghế
        self.seat_type_input = QComboBox()
        self.seat_type_input.addItems(['Ghế cứng', 'Ghế mềm', 'Giường nằm'])
        form_layout.addRow(QLabel('Loại ghế:'), self.seat_type_input)

        # Giá tiền
        self.price_input = QLineEdit()
        form_layout.addRow(QLabel('Giá tiền:'), self.price_input)

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
        train_trip = self.train_trip_input.text()
        station = self.station_input.text()
        seat_type = self.seat_type_input.currentText()
        price = self.price_input.text()

        # Xử lý dữ liệu (chỉ hiển thị tạm thời trong terminal)
        print(f"Tên khách hàng: {customer_name}")
        print(f"Chuyến tàu: {train_trip}")
        print(f"Ga tàu: {station}")
        print(f"Loại ghế: {seat_type}")
        print(f"Giá tiền: {price}")


# Tạo ứng dụng
app = QApplication(sys.argv)

# Tạo và hiển thị giao diện
window = TrainBookingApp()
window.show()

# Chạy ứng dụng
sys.exit(app.exec_())

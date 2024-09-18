import socket
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker, joinedload
from models import engine, HoaDon, ChiTietHoaDon, BangGia
from threading import Lock, Thread
from queue import Queue

# Khởi tạo session để làm việc với cơ sở dữ liệu
Session = sessionmaker(bind=engine)

# Lock để đảm bảo chỉ một yêu cầu được xử lý tại một thời điểm cho việc bán vé
sell_ticket_lock = Lock()

# Hàng đợi để xử lý các yêu cầu từ các ga
request_queue = Queue()

def sell_ticket(data):
    """
    Hàm thực hiện giao dịch bán vé.
    data: dict chứa thông tin từ client về vé cần bán
    """
    session = Session()
    with sell_ticket_lock:
        try:
            # Kiểm tra xem vé đã bán chưa
            existing_ticket = session.query(ChiTietHoaDon).filter_by(
                GheID=data['GheID'],
                TauID=data['TauID'],
                GaDi=data['GaDi'],
                GaDen=data['GaDen'],
                NgayKhoiHanh=datetime.strptime(data['NgayKhoiHanh'], '%Y-%m-%d %H:%M:%S')
            ).first()

            if existing_ticket:
                return {"status": "error", "message": "Vé đã được bán, vui lòng chọn vé khác."}

            # Tạo hóa đơn mới
            new_hoadon = HoaDon(
                TenKH=data['TenKH'],
                DiaChi=data['DiaChi'],
                SDT=data['SDT'],
                ThoiGian=datetime.now(),
                NhanVienID=1,  # Giả định nhân viên ID là 1
                SoTien=0  # Sẽ cập nhật sau
            )
            session.add(new_hoadon)
            session.commit()

            # Tạo chi tiết hóa đơn mới
            new_cthd = ChiTietHoaDon(
                GheID=data['GheID'],
                TauID=data['TauID'],
                GaDi=data['GaDi'],
                GaDen=data['GaDen'],
                HoaDonID=new_hoadon.HoaDonID,
                NgayKhoiHanh=datetime.strptime(data['NgayKhoiHanh'], '%Y-%m-%d %H:%M:%S')
            )
            session.add(new_cthd)

            # Cập nhật giá tiền từ bảng giá
            bang_gia = session.query(BangGia).filter_by(
                TauID=data['TauID'],
                GheID=data['GheID'],
                GaDi=data['GaDi'],
                GaDen=data['GaDen']
            ).first()

            if bang_gia:
                new_hoadon.SoTien = bang_gia.GiaTien
                session.commit()
                return {"status": "success", "message": "Giao dịch thành công."}
            else:
                session.rollback()
                return {"status": "error", "message": "Không tìm thấy giá vé."}

        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

def get_all_sold_tickets():
    """
    Hàm trả về tất cả các vé đã bán.
    """
    session = Session()
    try:
        # Truy vấn tất cả các vé đã bán từ bảng ChiTietHoaDon
        sold_tickets = session.query(ChiTietHoaDon).options(
            joinedload(ChiTietHoaDon.HoaDon),
            joinedload(ChiTietHoaDon.GaDi),
            joinedload(ChiTietHoaDon.GaDen),
            joinedload(ChiTietHoaDon.Ghe),
            joinedload(ChiTietHoaDon.Tau)
        ).all()

        # Biến đổi kết quả truy vấn thành danh sách dictionary
        tickets_list = []
        for ticket in sold_tickets:
            ticket_info = {
                "CTHDID": ticket.CTHDID,
                "GheID": ticket.GheID,
                "TauID": ticket.TauID,
                "GaDi": ticket.GaDi,
                "GaDen": ticket.GaDen,
                "NgayKhoiHanh": ticket.NgayKhoiHanh.strftime('%Y-%m-%d %H:%M:%S'),
                "HoaDonID": ticket.HoaDonID,
                "TenKH": ticket.HoaDon.TenKH,  # Lấy thông tin từ liên kết đến bảng HoaDon
                "SDT": ticket.HoaDon.SDT,
                "SoTien": ticket.HoaDon.SoTien,
                "TenGhe": ticket.Ghe.SoGhe if ticket.Ghe else None,
                "TenTau": ticket.Tau.TenTau if ticket.Tau else None,
                "GaDiTen": ticket.GaDi.Ten if ticket.GaDi else None,
                "GaDenTen": ticket.GaDen.Ten if ticket.GaDen else None,
            }
            tickets_list.append(ticket_info)

        return {"status": "success", "data": tickets_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        session.close()

def handle_request(action, data):
    """
    Hàm xử lý yêu cầu dựa trên loại hành động (action).
    """
    if action == "sell_ticket":
        return sell_ticket(data)
    elif action == "get_all_sold_tickets":
        return get_all_sold_tickets()
    else:
        return {"status": "error", "message": "Hành động không hợp lệ."}

def handle_requests():
    """
    Hàm xử lý các yêu cầu từ hàng đợi.
    """
    while True:
        action, data, connection = request_queue.get()
        response = handle_request(action, data)
        connection.send(json.dumps(response).encode('utf-8'))
        connection.close()
        request_queue.task_done()

def main():
    # Khởi tạo thread để xử lý hàng đợi
    Thread(target=handle_requests, daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 2704))
    sock.listen(5)
    print("Server đang lắng nghe tại 127.0.0.1:2704...")

    while True:
        connection, address = sock.accept()
        print(f"Nhận kết nối từ {address}")

        buf = connection.recv(1024)
        if buf:
            try:
                # Giải mã JSON từ client
                request = json.loads(buf.decode('utf-8'))

                # Kiểm tra và xử lý yêu cầu
                action = request.get("action")
                data = request.get("data", {})

                if action:
                    # Đưa yêu cầu vào hàng đợi để xử lý
                    request_queue.put((action, data, connection))
                else:
                    connection.send(json.dumps({"status": "error", "message": "Yêu cầu không hợp lệ."}).encode('utf-8'))
                    connection.close()

            except json.JSONDecodeError:
                connection.send(json.dumps({"status": "error", "message": "Dữ liệu không hợp lệ."}).encode('utf-8'))
                connection.close()

if __name__ == '__main__':
    main()

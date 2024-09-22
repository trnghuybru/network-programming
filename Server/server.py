import socket
import json
from  sqlalchemy import and_
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import IntegrityError
from threading import Thread
from queue import Queue
import logging

from models import Base, HoaDon, ChiTietHoaDon, BangGia, GioTau, Tuyen, Tau, Ga



HOST = "192.168.1.20"
PORT = 27047
# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Khởi tạo engine và session
engine = create_engine('mysql+pymysql://root@localhost/trainticketdb', pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)

# Hàng đợi để xử lý các yêu cầu từ các ga
request_queue = Queue()

def search_trains(tuyen_id, ngay_khoi_hanh):
    """
    Hàm tìm kiếm các chuyến tàu phù hợp dựa trên TuyenID và NgayKhoiHanh.
    """
    session = Session()
    try:
        start_of_day = datetime.strptime(ngay_khoi_hanh, '%Y-%m-%d')
        end_of_day = start_of_day + timedelta(days=1)

        # Truy vấn kết hợp các bảng GioTau, Tau, và Ga
        trains = session.query(GioTau, Tau, Ga).filter(
            and_(
                Tau.TuyenID == tuyen_id,
                GioTau.TauID == Tau.TauID,
                GioTau.GaID == Ga.GaID,
                GioTau.GioDi >= start_of_day,
                GioTau.GioDi < end_of_day
            )
        ).all()

        if not trains:
            return {"status": "error", "message": "Không có chuyến tàu phù hợp."}

        train_list = [{
            "TauID": tau.TauID,
            "TenTau": tau.TenTau,
            "GaDiID": ga.GaID,
            "GaDiTen": ga.Ten,
            "GioDi": gio_tau.GioDi.strftime('%Y-%m-%d %H:%M:%S'),
            "GioDen": gio_tau.GioDen.strftime('%Y-%m-%d %H:%M:%S')
        } for gio_tau, tau, ga in trains]

        return {"status": "success", "data": train_list}

    except Exception as e:
        logging.error(f"Lỗi khi tìm kiếm chuyến tàu: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi tìm kiếm chuyến tàu."}
    finally:
        session.close()

def book_ticket(data):
    """
    Hàm đặt vé sau khi đã chọn được chuyến tàu phù hợp.
    """
    session = Session()
    try:
        # Bắt đầu transaction với isolation level SERIALIZABLE
        session.begin()
        session.connection().execution_options(isolation_level="SERIALIZABLE")

        # Kiểm tra xem ghế đã được đặt chưa
        existing_ticket = session.query(ChiTietHoaDon).filter_by(
            GheID=data['GheID'],
            TauID=data['TauID'],
            NgayKhoiHanh=datetime.strptime(data['NgayKhoiHanh'], '%Y-%m-%d %H:%M:%S')
        ).with_for_update().first()

        if existing_ticket:
            session.rollback()
            return {"status": "error", "message": "Ghế này đã được đặt, vui lòng chọn ghế khác."}

        # Tạo hóa đơn mới
        new_hoadon = HoaDon(
            TenKH=data['TenKH'],
            DiaChi=data['DiaChi'],
            SDT=data['SDT'],
            ThoiGian=datetime.now(),
            NhanVienID=data['NhanVienID'],
            SoTien=0
        )
        session.add(new_hoadon)
        session.flush()

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
        ).with_for_update().first()

        if bang_gia:
            new_hoadon.SoTien = bang_gia.GiaTien
            session.commit()
            return {"status": "success", "message": "Đặt vé thành công.", "HoaDonID": new_hoadon.HoaDonID}
        else:
            session.rollback()
            return {"status": "error", "message": "Không tìm thấy giá vé."}

    except IntegrityError:
        session.rollback()
        return {"status": "error", "message": "Lỗi integrity, có thể do trùng lặp dữ liệu."}
    except Exception as e:
        session.rollback()
        logging.error(f"Lỗi khi đặt vé: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi xử lý đặt vé."}
    finally:
        session.close()

def get_all_routes():
    """
    Hàm lấy tất cả các tuyến từ cơ sở dữ liệu.
    """
    session = Session()
    try:
        # Truy vấn tất cả các tuyến từ bảng 'Tuyen'
        routes = session.query(Tuyen).all()

        # Nếu không tìm thấy tuyến nào, trả về thông báo lỗi
        if not routes:
            return {"status": "error", "message": "Không có tuyến nào trong hệ thống."}

        # Tạo danh sách các tuyến
        route_list = [{
            "TuyenID": route.TuyenID,
            "Ten": route.Ten,
            "Huong": route.Huong
        } for route in routes]

        return {"status": "success", "data": route_list}

    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách các tuyến: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi lấy danh sách các tuyến."}
    finally:
        session.close()

def handle_request(action, data):
    """
    Hàm xử lý yêu cầu dựa trên loại hành động (action).
    """
    if action == "search_trains":
        return search_trains(data['TuyenID'], data['NgayKhoiHanh'])
    elif action == "book_ticket":
        return book_ticket(data)
    elif action == "get_all_routes":  # Đã thay đổi từ "get_all_stations"
        return get_all_routes()
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
    sock.bind((HOST,PORT))
    sock.listen()
    logging.info("Server đang lắng nghe tại 127.0.0.1:2704...")

    while True:
        connection, address = sock.accept()
        logging.info(f"Nhận kết nối từ {address}")

        try:
            buf = connection.recv(1024)
            if buf:
                request = json.loads(buf.decode('utf-8'))
                action = request.get("action")
                data = request.get("data", {})

                if action:
                    request_queue.put((action, data, connection))
                else:
                    connection.send(json.dumps({"status": "error", "message": "Yêu cầu không hợp lệ."}).encode('utf-8'))
                    connection.close()

        except json.JSONDecodeError:
            connection.send(json.dumps({"status": "error", "message": "Dữ liệu không hợp lệ."}).encode('utf-8'))
            connection.close()
        except Exception as e:
            logging.error(f"Lỗi xử lý kết nối: {str(e)}")
            connection.send(json.dumps({"status": "error", "message": "Đã xảy ra lỗi server."}).encode('utf-8'))
            connection.close()

if __name__ == '__main__':
    main()
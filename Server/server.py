import socket
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import IntegrityError
from threading import Thread
from queue import Queue
import logging

from models import Base, HoaDon, ChiTietHoaDon, BangGia, GioTau, Ga, Tau, Ghe

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Khởi tạo engine và session
engine = create_engine('mysql+pymysql://root@localhost/trainticketdb', pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)

# Hàng đợi để xử lý các yêu cầu từ các ga
request_queue = Queue()

def search_trains(ga_di_id, ga_den_id, ngay_di):
    """
    Hàm tìm kiếm các chuyến tàu phù hợp.
    """
    session = Session()
    try:
        start_of_day = datetime.strptime(ngay_di, '%Y-%m-%d')
        end_of_day = start_of_day + timedelta(days=1)

        trains = session.query(GioTau).filter(
            GioTau.GaID == ga_di_id,
            GioTau.GaDen == ga_den_id,
            GioTau.GioDi >= start_of_day,
            GioTau.GioDi < end_of_day
        ).options(
            joinedload(GioTau.Tau),
            joinedload(GioTau.Ga)
        ).all()

        if not trains:
            return {"status": "error", "message": "Không có chuyến tàu phù hợp."}

        train_list = [{
            "TauID": train.TauID,
            "TenTau": train.Tau.TenTau,
            "GaDiID": train.GaID,
            "GaDiTen": train.Ga.Ten,
            "GioDi": train.GioDi.strftime('%Y-%m-%d %H:%M:%S'),
            "GioDen": train.GioDen.strftime('%Y-%m-%d %H:%M:%S')
        } for train in trains]

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

def handle_request(action, data):
    """
    Hàm xử lý yêu cầu dựa trên loại hành động (action).
    """
    if action == "search_trains":
        return search_trains(data['GaDi'], data['GaDen'], data['NgayDi'])
    elif action == "book_ticket":
        return book_ticket(data)
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
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

from models import HoaDon, ChiTietHoaDon, BangGia, GioTau, Tuyen, Tau, Ga, Toa, TauToa, Ghe



HOST = "192.168.1.10"
PORT = 27049

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Khởi tạo engine và session
engine = create_engine('mysql+pymysql://root@localhost/trainticketdb', pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)

# Hàng đợi để xử lý các yêu cầu từ các ga
request_queue = Queue()

def search_trains(tuyen_id, ngay_khoi_hanh):
    session = Session()
    try:
        start_of_day = datetime.strptime(ngay_khoi_hanh, '%Y-%m-%d')
        end_of_day = start_of_day + timedelta(days=1)

        print(f"Start of day: {start_of_day}, End of day: {end_of_day}")

        # Truy vấn kết hợp các bảng GioTau, Tau, và Ga
        trains = session.query(GioTau, Tau, Ga).join(
            Tau, GioTau.TauID == Tau.TauID
        ).join(
            Ga, GioTau.GaID == Ga.GaID
        ).filter(
            Tau.TuyenID == tuyen_id,
            GioTau.GioDi >= start_of_day,
            GioTau.GioDi < end_of_day
        ).all()

        if not trains:
            print("Không có chuyến tàu phù hợp.")
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

def print_carriages(train_id):
    session = Session()
    try:
        # Truy vấn để lấy thông tin các toa của chuyến tàu
        carriages = session.query(Toa).join(TauToa).filter(TauToa.TauID == train_id).all()

        if not carriages:
            print("Không có toa nào trong chuyến tàu này.")
            return {"status": "error", "message": "Không có toa nào trong chuyến tàu này."}

        carriage_list = [{
            "ToaID": toa.ToaID,
            "TenToa": toa.TenToa
        } for toa in carriages]

        print("Các toa trong chuyến tàu:")
        for carriage in carriage_list:
            print(f"ToaID: {carriage['ToaID']}, TenToa: {carriage['TenToa']}")

        return {"status": "success", "data": carriage_list}

    except Exception as e:
        logging.error(f"Lỗi khi lấy thông tin các toa: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi lấy thông tin các toa."}
    finally:
        session.close()

def print_seats_in_carriage(toa_id, ngay_khoi_hanh):
    session = Session()
    try:
        # Lấy tất cả các ghế trong toa đã chọn
        seats = session.query(Ghe).filter(Ghe.ToaID == toa_id).all()

        if not seats:
            print("Không có ghế nào trong toa này.")
            return {"status": "error", "message": "Không có ghế nào trong toa này."}

        # Lấy danh sách các ghế đã được đặt trong toa này cho ngày khởi hành cụ thể
        booked_seats = session.query(ChiTietHoaDon.GheID).filter(
            ChiTietHoaDon.TauID == TauToa.TauID,  # Tìm chuyến tàu phù hợp với Toa
            ChiTietHoaDon.GheID == Ghe.GheID,    # Kết hợp bảng Ghe và ChiTietHoaDon
            ChiTietHoaDon.NgayKhoiHanh == ngay_khoi_hanh
        ).filter(Ghe.ToaID == toa_id).all()

        # Tạo một set chứa các ghế đã đặt để dễ kiểm tra
        booked_seat_ids = {seat.GheID for seat in booked_seats}

        # In danh sách các ghế và trạng thái đặt
        seat_list = []
        for seat in seats:
            status = 1 if seat.GheID in booked_seat_ids else 0  # 1 là đã đặt, 0 là chưa đặt
            seat_list.append({
                "GheID": seat.GheID,
                "SoGhe": seat.SoGhe,
                "TrangThai": status
            })
            print(f"GheID: {seat.GheID}, SoGhe: {seat.SoGhe}, TrangThai: {status}")

        return {"status": "success", "data": seat_list}

    except Exception as e:
        logging.error(f"Lỗi khi lấy thông tin ghế: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi lấy thông tin ghế."}
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


def get_start_and_destination_stations(tau_id):
    session = Session(bind=engine)
    try:
        # Truy vấn dữ liệu
        ga_di_va_ga_den = session.query(
            GioTau.GioID,
            Ga.Ten.label("GaDi"),
            BangGia.GaDi.label("GaDiID"),  # ID của ga đi
            Ga.Ten.label("GaDen"),
            GioTau.GaID.label("GaDenID"),  # ID của ga đến (từ GioTau)
            GioTau.GioDi,
            GioTau.GioDen
        ).join(
            BangGia, GioTau.TauID == BangGia.TauID  # Liên kết với bảng BangGia
        ).join(
            Ga, BangGia.GaDi == Ga.GaID  # Lấy tên ga đi
        ).join(
            Ga, GioTau.GaID == Ga.GaID  # Lấy tên ga đến
        ).filter(
            GioTau.TauID == tau_id
        ).distinct().all()

        if not ga_di_va_ga_den:
            return {"status": "error", "message": "Không có ga đi hoặc ga đến nào cho tàu này."}

        # Chuyển dữ liệu thành danh sách dễ sử dụng
        ga_list = []
        for ga in ga_di_va_ga_den:
            ga_list.append({
                "GioID": ga.GioID,
                "GaDi": ga.GaDi,
                "GaDiID": ga.GaDiID,  # ID của ga đi từ BangGia
                "GioDi": ga.GioDi,
                "GaDen": ga.GaDen,
                "GaDenID": GioTau.GaID,  # ID của ga đến từ GioTau
                "GioDen": ga.GioDen
            })

        return {"status": "success", "data": ga_list}

    except Exception as e:
        logging.error(f"Lỗi khi truy vấn ga: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi truy vấn ga đi và ga đến."}
    finally:
        session.close()


def get_price(tau_id, ga_di_id, ga_den_id, ghe_id):
    session = Session(bind=engine)
    try:
        # Truy vấn bảng BangGia để lấy giá tiền dựa trên ga đi, ga đến, tàu và ghế
        gia_tien = session.query(BangGia.GiaTien).filter(
            BangGia.TauID == tau_id,
            BangGia.GaDi == ga_di_id,
            BangGia.GaDen == ga_den_id,
            BangGia.GheID == ghe_id
        ).first()

        if not gia_tien:
            return {"status": "error", "message": "Không tìm thấy giá tiền cho chuyến đi này."}

        return {"status": "success", "gia_tien": gia_tien.GiaTien}

    except Exception as e:
        logging.error(f"Lỗi khi lấy giá tiền: {str(e)}")
        return {"status": "error", "message": "Đã xảy ra lỗi khi lấy giá tiền."}
    finally:
        session.close()


def seat_locking(tau_id, ghe_id, ngay_khoi_hanh):
    """
    Hàm này khóa ghế đã chọn trên chuyến tàu, đảm bảo rằng ghế không bị đặt trùng.

    Parameters:
    tau_id (int): ID của tàu.
    ghe_id (int): ID của ghế.
    ngay_khoihanh (datetime): Ngày khởi hành của chuyến tàu.

    Returns:
    dict: Trả về kết quả thành công hoặc lỗi.
    """

    session = Session(bind=engine)
    try:
        # Bắt đầu giao dịch
        session.begin()

        # Truy vấn ghế với khóa
        ghe = session.query(Ghe).filter(
            Ghe.GheID == ghe_id
        ).with_for_update().first()

        if not ghe:
            return {"status": "error", "message": "Ghế không tồn tại."}

        # Kiểm tra xem ghế đã được đặt cho chuyến tàu này vào ngày khởi hành này chưa
        is_booked = session.query(ChiTietHoaDon).filter(
            and_(
                ChiTietHoaDon.GheID == ghe_id,
                ChiTietHoaDon.TauID == tau_id,
                ChiTietHoaDon.NgayKhoiHanh == ngay_khoi_hanh
            )
        ).first()

        if is_booked:
            return {"status": "error", "message": "Ghế đã được đặt cho chuyến tàu này."}

        # Nếu chưa đặt, khóa thành công và chờ thêm thông tin hóa đơn hoặc các hành động tiếp theo
        return {"status": "success", "message": "Ghế đã được khóa thành công."}

    except IntegrityError as e:
        session.rollback()
        return {"status": "error", "message": f"Lỗi khóa ghế: {str(e)}"}

    except Exception as e:
        session.rollback()
        return {"status": "error", "message": f"Đã xảy ra lỗi: {str(e)}"}

    finally:
        session.close()


def place_ticket_order(tuyen_id, tau_id, ga_di, ga_den, ngay_khoi_hanh, ten_kh, dia_chi, sdt, nhan_vien_id, ghe_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tạo hóa đơn
    hoa_don = HoaDon(
        TenKH=ten_kh,
        DiaChi=dia_chi,
        SDT=sdt,
        NhanVienID=nhan_vien_id,
        SoTien=0.0  # Cần cập nhật sau khi tính tiền
    )

    session.add(hoa_don)
    session.flush()  # Để lấy HoaDonID sau khi thêm

    # Tạo chi tiết hóa đơn
    chi_tiet = ChiTietHoaDon(
        GheID=ghe_id,
        TauID=tau_id,
        GaDi=ga_di,
        GaDen=ga_den,
        HoaDonID=hoa_don.HoaDonID,
        NgayKhoiHanh=ngay_khoi_hanh
    )

    session.add(chi_tiet)

    try:
        session.commit()  # Cam kết thay đổi vào cơ sở dữ liệu
        print("Đặt vé thành công!")
    except IntegrityError:
        session.rollback()  # Hoàn tác nếu có lỗi
        print("Đặt vé không thành công! Có lỗi xảy ra.")
    finally:
        session.close()

def handle_request(action, data):
    """
    Hàm xử lý yêu cầu dựa trên loại hành động (action).
    """
    if action == "search_trains":
        return search_trains(data['TuyenID'], data['NgayKhoiHanh'])
    elif action == "book_ticket":
        return place_ticket_order(
            tuyen_id=data['TuyenID'],
            tau_id=data['TauID'],
            ga_di=data['GaDi'],
            ga_den=data['GaDen'],
            ngay_khoi_hanh=data['NgayKhoiHanh'],
            ten_kh=data['TenKH'],
            dia_chi=data['DiaChi'],
            sdt=data['SDT'],
            nhan_vien_id=data['NhanVienID'],
            ghe_id=data['GheID']
        )
    elif action == "get_all_routes":
        return get_all_routes()
    elif action == "print_carriages":
        return print_carriages(data['tau_id'])
    elif action == "get_seats_in_carriage":
        return print_seats_in_carriage(data['toa_id'], data['ngay_khoi_hanh'])
    elif action == "get_start_and_destination_stations":
        return get_start_and_destination_stations(data['tau_id'])
    elif action == "get_price":
        return get_price(data['tau_id'], data['ga_di_id'], data['ga_den_id'], data['ghe_id'])
    elif action == "seat_locking":
        return seat_locking(data['tau_id'], data['ghe_id'], data['ngay_khoi_hanh'])
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
    logging.info(f"Server đang lắng nghe tại {HOST}:{PORT}")

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
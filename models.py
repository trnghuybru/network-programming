from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Khởi tạo engine và base
engine = create_engine('mysql+pymysql://root@localhost/trainticketdb')
Base = declarative_base()

# Định nghĩa các bảng
class BangGia(Base):
    __tablename__ = 'banggia'
    BangGiaID = Column(Integer, primary_key=True)
    TauID = Column(Integer, nullable=False)
    GheID = Column(Integer, nullable=False)
    GaDi = Column(Integer, nullable=False)
    GaDen = Column(Integer, nullable=False)
    GiaTien = Column(Float, nullable=False)

class ChiTietHoaDon(Base):
    __tablename__ = 'chitiethoadon'
    CTHDID = Column(Integer, primary_key=True)
    GheID = Column(Integer, nullable=False)
    TauID = Column(Integer, nullable=False)
    GaDi = Column(Integer, ForeignKey('ga.GaID'), nullable=False)
    GaDen = Column(Integer, nullable=False)
    HoaDonID = Column(Integer, ForeignKey('hoadon.HoaDonID'), nullable=False)
    NgayKhoiHanh = Column(DateTime, nullable=False)

class Ga(Base):
    __tablename__ = 'ga'
    GaID = Column(Integer, primary_key=True)
    Ten = Column(String(200), nullable=False)
    DiaChi = Column(String(200), nullable=False)
    SDT = Column(String(11), nullable=False)

class Ghe(Base):
    __tablename__ = 'ghe'
    GheID = Column(Integer, primary_key=True)
    SoGhe = Column(Integer, nullable=False)
    LoaiGheID = Column(Integer, ForeignKey('loaighe.LoaiGheID'), nullable=False)
    ToaID = Column(Integer, ForeignKey('toa.ToaID'), nullable=False)

class GioTau(Base):
    __tablename__ = 'giotau'
    GioID = Column(Integer, primary_key=True)
    GaID = Column(Integer, ForeignKey('ga.GaID'), nullable=False)
    TauID = Column(Integer, ForeignKey('tau.TauID'), nullable=False)
    GioDi = Column(DateTime, nullable=False)
    GioDen = Column(DateTime, nullable=False)

class HoaDon(Base):
    __tablename__ = 'hoadon'
    HoaDonID = Column(Integer, primary_key=True, autoincrement=True)
    TenKH = Column(String(50), nullable=False)
    DiaChi = Column(String(200), nullable=False)
    SDT = Column(String(11), nullable=False)
    ThoiGian = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP')
    NhanVienID = Column(Integer, ForeignKey('nhanvien.NhanVienID'), nullable=False)
    SoTien = Column(Float, nullable=False)

class LoaiGhe(Base):
    __tablename__ = 'loaighe'
    LoaiGheID = Column(Integer, primary_key=True)
    Ten = Column(String(50), nullable=False)

class NhanVien(Base):
    __tablename__ = 'nhanvien'
    NhanVienID = Column(Integer, primary_key=True)
    Ten = Column(String(50), nullable=False)
    SDT = Column(String(11), nullable=False)
    Email = Column(String(255), unique=True, nullable=False)
    Password = Column(String(255), nullable=False)

class Tau(Base):
    __tablename__ = 'tau'
    TauID = Column(Integer, primary_key=True)
    TenTau = Column(String(255), nullable=False)
    TuyenID = Column(Integer, ForeignKey('tuyen.TuyenID'), nullable=False)

class TauToa(Base):
    __tablename__ = 'tautoa'
    TauToaID = Column(Integer, primary_key=True)
    TauID = Column(Integer, ForeignKey('tau.TauID'), nullable=False)
    ToaID = Column(Integer, ForeignKey('toa.ToaID'), nullable=False)

class Toa(Base):
    __tablename__ = 'toa'
    ToaID = Column(Integer, primary_key=True)
    TenToa = Column(String(50), nullable=False)

class Tuyen(Base):
    __tablename__ = 'tuyen'
    TuyenID = Column(Integer, primary_key=True)
    Ten = Column(String(255), nullable=False)
    Huong = Column(String(255), nullable=False)

# Tạo các bảng trong cơ sở dữ liệu
Base.metadata.create_all(engine)

# Khởi tạo session để làm việc với cơ sở dữ liệu
Session = sessionmaker(bind=engine)
session = Session()

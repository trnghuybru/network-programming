-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th9 09, 2024 lúc 11:35 AM
-- Phiên bản máy phục vụ: 10.4.28-MariaDB
-- Phiên bản PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `trainticketdb`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `banggia`
--

CREATE TABLE `banggia` (
  `BangGiaID` int(11) NOT NULL,
  `TauID` int(11) NOT NULL,
  `GheID` int(11) NOT NULL,
  `GaDi` int(11) NOT NULL,
  `GaDen` int(11) NOT NULL,
  `GiaTien` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chitiethoadon`
--

CREATE TABLE `chitiethoadon` (
  `CTHDID` int(11) NOT NULL,
  `GheID` int(11) NOT NULL,
  `TauID` int(11) NOT NULL,
  `GaDi` int(11) NOT NULL,
  `GaDen` int(11) NOT NULL,
  `HoaDonID` int(11) NOT NULL,
  `NgayKhoiHanh` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `ga`
--

CREATE TABLE `ga` (
  `GaID` int(11) NOT NULL,
  `Ten` varchar(200) NOT NULL,
  `DiaChi` varchar(200) NOT NULL,
  `SDT` varchar(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `ghe`
--

CREATE TABLE `ghe` (
  `GheID` int(11) NOT NULL,
  `SoGhe` int(11) NOT NULL,
  `LoaiGheID` int(11) NOT NULL,
  `ToaID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `giotau`
--

CREATE TABLE `giotau` (
  `GioID` int(11) NOT NULL,
  `GaID` int(11) NOT NULL,
  `TauID` int(11) NOT NULL,
  `GioDi` datetime NOT NULL,
  `GioDen` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `hoadon`
--

CREATE TABLE `hoadon` (
  `HoaDonID` int(11) NOT NULL,
  `TenKH` varchar(50) NOT NULL,
  `DiaChi` varchar(200) NOT NULL,
  `SDT` varchar(11) NOT NULL,
  `ThoiGian` datetime NOT NULL DEFAULT current_timestamp(),
  `NhanVienID` int(11) NOT NULL,
  `SoTien` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `loaighe`
--

CREATE TABLE `loaighe` (
  `LoaiGheID` int(11) NOT NULL,
  `Ten` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhanvien`
--

CREATE TABLE `nhanvien` (
  `NhanVienID` int(11) NOT NULL,
  `Ten` varchar(50) NOT NULL,
  `SDT` varchar(11) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `Password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tau`
--

CREATE TABLE `tau` (
  `TauID` int(11) NOT NULL,
  `TenTau` varchar(255) NOT NULL,
  `TuyenID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tautoa`
--

CREATE TABLE `tautoa` (
  `TauToaID` int(11) NOT NULL,
  `TauID` int(11) NOT NULL,
  `ToaID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `toa`
--

CREATE TABLE `toa` (
  `ToaID` int(11) NOT NULL,
  `TenToa` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tuyen`
--

CREATE TABLE `tuyen` (
  `TuyenID` int(11) NOT NULL,
  `Ten` varchar(255) NOT NULL,
  `Huong` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `banggia`
--
ALTER TABLE `banggia`
  ADD PRIMARY KEY (`BangGiaID`),
  ADD KEY `GaDen` (`GaDen`),
  ADD KEY `banggia_ibfk_1` (`GaDi`),
  ADD KEY `GheID` (`GheID`);

--
-- Chỉ mục cho bảng `chitiethoadon`
--
ALTER TABLE `chitiethoadon`
  ADD PRIMARY KEY (`CTHDID`),
  ADD KEY `GheID` (`GheID`),
  ADD KEY `chitiethoadon_ibfk_1` (`TauID`),
  ADD KEY `GaDen` (`GaDen`),
  ADD KEY `HoaDonID` (`HoaDonID`),
  ADD KEY `GaDi` (`GaDi`);

--
-- Chỉ mục cho bảng `ga`
--
ALTER TABLE `ga`
  ADD PRIMARY KEY (`GaID`);

--
-- Chỉ mục cho bảng `ghe`
--
ALTER TABLE `ghe`
  ADD PRIMARY KEY (`GheID`),
  ADD KEY `LoaiGheID` (`LoaiGheID`),
  ADD KEY `ghe_ibfk_1` (`ToaID`);

--
-- Chỉ mục cho bảng `giotau`
--
ALTER TABLE `giotau`
  ADD PRIMARY KEY (`GioID`),
  ADD KEY `GaID` (`GaID`),
  ADD KEY `giotau_ibfk_1` (`TauID`);

--
-- Chỉ mục cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  ADD PRIMARY KEY (`HoaDonID`),
  ADD KEY `NhanVienID` (`NhanVienID`);

--
-- Chỉ mục cho bảng `loaighe`
--
ALTER TABLE `loaighe`
  ADD PRIMARY KEY (`LoaiGheID`);

--
-- Chỉ mục cho bảng `nhanvien`
--
ALTER TABLE `nhanvien`
  ADD PRIMARY KEY (`NhanVienID`),
  ADD UNIQUE KEY `Email` (`Email`);

--
-- Chỉ mục cho bảng `tau`
--
ALTER TABLE `tau`
  ADD PRIMARY KEY (`TauID`),
  ADD KEY `TuyenID` (`TuyenID`);

--
-- Chỉ mục cho bảng `tautoa`
--
ALTER TABLE `tautoa`
  ADD PRIMARY KEY (`TauToaID`),
  ADD KEY `TauID` (`TauID`),
  ADD KEY `tautoa_ibfk_1` (`ToaID`);

--
-- Chỉ mục cho bảng `toa`
--
ALTER TABLE `toa`
  ADD PRIMARY KEY (`ToaID`);

--
-- Chỉ mục cho bảng `tuyen`
--
ALTER TABLE `tuyen`
  ADD PRIMARY KEY (`TuyenID`) USING BTREE;

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  MODIFY `HoaDonID` int(11) NOT NULL AUTO_INCREMENT;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `chitiethoadon`
--
ALTER TABLE `chitiethoadon`
  ADD CONSTRAINT `chitiethoadon_ibfk_1` FOREIGN KEY (`HoaDonID`) REFERENCES `hoadon` (`HoaDonID`),
  ADD CONSTRAINT `chitiethoadon_ibfk_2` FOREIGN KEY (`GaDi`) REFERENCES `ga` (`GaID`);

--
-- Các ràng buộc cho bảng `ghe`
--
ALTER TABLE `ghe`
  ADD CONSTRAINT `ghe_ibfk_1` FOREIGN KEY (`ToaID`) REFERENCES `toa` (`ToaID`);

--
-- Các ràng buộc cho bảng `giotau`
--
ALTER TABLE `giotau`
  ADD CONSTRAINT `giotau_ibfk_1` FOREIGN KEY (`TauID`) REFERENCES `tau` (`TauID`);

--
-- Các ràng buộc cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  ADD CONSTRAINT `hoadon_ibfk_1` FOREIGN KEY (`NhanVienID`) REFERENCES `nhanvien` (`NhanVienID`);

--
-- Các ràng buộc cho bảng `tau`
--
ALTER TABLE `tau`
  ADD CONSTRAINT `tau_ibfk_1` FOREIGN KEY (`TuyenID`) REFERENCES `tuyen` (`TuyenID`);

--
-- Các ràng buộc cho bảng `tautoa`
--
ALTER TABLE `tautoa`
  ADD CONSTRAINT `tautoa_ibfk_1` FOREIGN KEY (`ToaID`) REFERENCES `toa` (`ToaID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

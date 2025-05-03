# Ứng Dụng Client Giá Vàng

Ứng dụng React hiển thị thông tin giá vàng theo thời gian thực từ server.

## Tính Năng

- Hiển thị giá vàng từ server với cập nhật theo thời gian thực
- Giao diện hiện đại với Material UI
- Bảng giá chi tiết với hiệu ứng highlight khi giá thay đổi
- Card hiển thị giá mua/bán cho từng loại vàng
- Thích ứng với nhiều kích thước màn hình (responsive)

## Cấu Trúc

```
client/
├── public/                 # Tài nguyên tĩnh
├── src/
│   ├── components/         # Các component React
│   │   ├── GoldPriceCard.js    # Card hiển thị giá từng loại vàng
│   │   ├── GoldPriceTable.js   # Bảng giá chi tiết
│   │   └── Header.js           # Header ứng dụng
│   ├── App.js              # Component chính của ứng dụng
│   └── index.js            # Điểm khởi đầu React
└── package.json            # Cấu hình và dependencies
```

## Kết Nối Với Server

Ứng dụng sử dụng Socket.IO để nhận cập nhật thời gian thực từ server:

1. **Kết nối ban đầu**: Khi ứng dụng khởi động, một kết nối Socket.IO được thiết lập với server
2. **Dữ liệu ban đầu**: Ứng dụng gọi API REST để lấy dữ liệu giá vàng ban đầu
3. **Cập nhật thời gian thực**: Ứng dụng lắng nghe sự kiện `gold-prices-updated` để nhận dữ liệu mới
4. **Hiệu ứng trực quan**: Khi có dữ liệu mới, các thành phần giao diện cập nhật với hiệu ứng highlight

## Công Nghệ Sử Dụng

- **React**: Thư viện UI chính
- **Material UI**: Framework component UI
- **Socket.IO Client**: Kết nối thời gian thực với server
- **Axios**: Gọi API HTTP

## Cài Đặt và Chạy

1. Cài đặt dependencies:
```
npm install
```

2. Chạy ứng dụng:
```
npm start
```

Ứng dụng sẽ chạy ở địa chỉ [http://localhost:3000](http://localhost:3000)

## Liên Kết Với Server

Đảm bảo server đang chạy ở địa chỉ http://localhost:3010 để ứng dụng client có thể kết nối và nhận dữ liệu.

---
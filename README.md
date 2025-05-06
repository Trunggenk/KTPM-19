# Ứng dụng Theo dõi Giá Vàng Thời Gian Thực

Ứng dụng này cho phép người dùng theo dõi giá vàng Việt Nam theo thời gian thực, với các loại vàng khác nhau bao gồm SJC, vàng nhẫn SJC, và vàng các loại 24K, 18K, 14K, 9K.


## Cấu trúc ứng dụng

Ứng dụng được chia thành hai phần chính:

1. **Server (Port 3010)**: 
   - Chịu trách nhiệm lưu trữ và quản lý dữ liệu giá vàng
   - Cung cấp API và giao diện admin
   - Xử lý các request từ client API

2. **Client (Port 3005)**: 
   - Ứng dụng web hiển thị giá vàng cho người dùng cuối
   - Kiến trúc 3 tầng:
     - `api.js`: Giao tiếp trực tiếp với server
     - `app.js`: Logic nghiệp vụ, xử lý dữ liệu 
     - Frontend: Hiển thị dữ liệu cho người dùng

### Kiến trúc Client

Client được xây dựng theo mô hình 3 tầng:

1. **Data Access Layer** (`api.js`):
   - Chịu trách nhiệm giao tiếp với server
   - Xử lý các request và response từ server
   - Cung cấp interface thống nhất cho việc truy cập dữ liệu

2. **Business Logic Layer** (`app.js`):
   - Chứa logic nghiệp vụ của ứng dụng
   - Sử dụng các hàm từ `api.js` để lấy dữ liệu
   - Xử lý dữ liệu trước khi trả về cho frontend

3. **Presentation Layer** (`public/app.js` + `public/index.html`):
   - Hiển thị dữ liệu cho người dùng
   - Xử lý tương tác người dùng
   - Cập nhật giao diện theo thời gian thực

## Công nghệ sử dụng

- **Backend**: Express.js (Node.js)
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript thuần

## Hướng dẫn cài đặt

### Server

```bash
# Di chuyển vào thư mục server
cd server

# Cài đặt các gói liên quan
npm install

# Tạo folder cho database
mkdir -p db

# Khởi chạy server
npm start
```

### Client

```bash
# Di chuyển vào thư mục client
cd client

# Cài đặt các gói liên quan
npm install

# Khởi chạy client
npm start
```

## Chạy bộ mô phỏng giá vàng

Để chạy bộ mô phỏng cập nhật giá vàng (thay thế cho API thực tế), sử dụng lệnh sau:

```bash
# Di chuyển vào thư mục server
cd server

# Chạy bộ mô phỏng
npm run simulate
```

## Sử dụng ứng dụng

### Xem giá vàng (Client)

1. Mở trình duyệt và truy cập `http://localhost:3005`
2. Trang web sẽ tự động cập nhật giá vàng mỗi 2 giây
3. Khi giá vàng thay đổi, các phần tử sẽ được highlight và hiển thị mức thay đổi

### Quản lý giá vàng (Server Admin)

1. Mở trình duyệt và truy cập `http://localhost:3010/admin`
2. Trang admin hiển thị giá vàng hiện tại và cho phép cập nhật giá mới
3. Nhập giá mới và nhấn nút "Cập nhật giá vàng" để lưu thay đổi

## API Endpoints

| Endpoint | Phương thức | Mục tiêu |
|----------|:-----------:|----------|
| /api/add | POST | Thêm/chỉnh sửa giá trị trong database |
| /api/get/:id | GET | Trả về giá trị của một key |
| /api/gold-prices | GET | Trả về giá của tất cả các loại vàng |
| /api/update-gold | POST | Cập nhật giá vàng |
| /admin | GET | Trang web quản lý giá vàng |

## Yêu cầu triển khai
| Mức độ | Mô tả |
|--|--|
| ![Static Badge](https://img.shields.io/badge/OPTIONAL-medium-yellow)  | Tối ưu chương trình trên |
| ![Static Badge](https://img.shields.io/badge/OPTIONAL-easy-green) | Bổ sung giao diện web hoàn chỉnh hơn |
| ![Static Badge](https://img.shields.io/badge/OPTIONAL-easy-green) | Thay thế cơ sở dữ liệu hiện tại |
| ![Static Badge](https://img.shields.io/badge/REQUIRED-easy-green) | Thay thế công nghệ sử dụng cho việc gọi request liên tục trong `viewer.html` (VD: socket.io, ...) |
| ![Static Badge](https://img.shields.io/badge/REQUIRED-medium-yellow) | Thêm lớp persistent bằng cách sử dụng ORM (Object-Relational Mapping) |
| ![Static Badge](https://img.shields.io/badge/REQUIRED-medium-yellow) | Triển khai theo kiến trúc Publisher-Subscriber và cài đặt message broker tuỳ chọn |
| ![Static Badge](https://img.shields.io/badge/REQUIRED-medium-yellow) | Nêu các vấn đề chương trình gốc đang gặp phải về các thuộc tính chất lượng và *đánh giá* hiệu năng sau khi nâng cấp |

Ngoài ra, các bạn có thể tuỳ chọn bổ sung thêm một số phần triển khai khác.


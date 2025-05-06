# Ứng dụng Theo dõi Giá Vàng Thời Gian Thực

Ứng dụng này cho phép người dùng theo dõi giá vàng Việt Nam theo thời gian thực, với các loại vàng khác nhau bao gồm SJC, vàng nhẫn SJC, và vàng các loại 24K, 18K, 14K, 9K.

## Tính năng

- Hiển thị giá vàng theo thời gian thực với cập nhật tự động
- Theo dõi thay đổi giá (tăng/giảm) với hiệu ứng trực quan
- Giao diện đẹp, thân thiện với người dùng và responsive
- Cập nhật dữ liệu mỗi 2 giây

## Công nghệ sử dụng

- **Backend**: Express.js (Node.js)
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript thuần

## Hướng dẫn cài đặt

```bash
# Cài đặt các gói liên quan
npm install

# Tạo folder cho database
mkdir -p db

# Khởi chạy ứng dụng
npm start
```

## Chạy bộ mô phỏng giá vàng

Để chạy bộ mô phỏng cập nhật giá vàng (thay thế cho API thực tế), sử dụng lệnh sau trong một terminal khác:

```bash
npm run simulate
```

## Sử dụng ứng dụng

1. Mở trình duyệt và truy cập `http://localhost:8080/gold`
2. Trang web sẽ tự động cập nhật giá vàng mỗi 2 giây
3. Khi giá vàng thay đổi, các phần tử sẽ được highlight và hiển thị mức thay đổi

## API Endpoints

| Endpoint | Phương thức | Mục tiêu |
|----------|:-----------:|----------|
| /add | POST | Thêm/chỉnh sửa giá trị trong database |
| /get/:id | GET | Trả về giá trị của một key |
| /gold-prices | GET | Trả về giá của tất cả các loại vàng |
| /update-gold | POST | Cập nhật giá vàng |
| /gold | GET | Trang web theo dõi giá vàng |
| /viewer/:id | GET | Trang web theo dõi giá trị của một key |


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


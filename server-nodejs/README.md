# Kiến Trúc Server

## Tổng Quan

Hệ thống server là một ứng dụng Node.js sử dụng Express, Socket.IO và Redis để cung cấp thông tin giá vàng theo thời gian thực. Server thu thập dữ liệu từ API bên ngoài, lưu trữ vào cơ sở dữ liệu SQLite, và phát sóng các cập nhật đến client thông qua WebSocket.

## Công Nghệ Sử Dụng

- **Express**: Framework web để xây dựng API REST
- **Socket.IO**: Cung cấp kết nối WebSocket cho cập nhật thời gian thực
- **Redis**: Hệ thống pub/sub để truyền thông giữa các dịch vụ
- **Sequelize**: ORM để tương tác với cơ sở dữ liệu SQLite
- **SQLite**: Cơ sở dữ liệu nhẹ để lưu trữ dữ liệu giá vàng

## Kiến Trúc Mã Nguồn

### Cấu Trúc Thư Mục

```
server/
├── controllers/      # Xử lý logic nghiệp vụ
├── db/               # Chứa file cơ sở dữ liệu SQLite
├── models/           # Định nghĩa các model dữ liệu
├── public/           # Tài nguyên tĩnh (nếu có)
├── routes/           # Định nghĩa API routes
├── services/         # Các dịch vụ ứng dụng (Redis, Socket.IO)
└── server.js         # Điểm khởi đầu ứng dụng
```

### Luồng Dữ Liệu

1. **Thu thập dữ liệu**: Server định kỳ (mỗi 5 giây) gọi API bên ngoài để lấy thông tin giá vàng mới nhất
2. **Phát sóng dữ liệu**: Dữ liệu được publish lên 2 kênh Redis: 'gold-prices' và 'gold-prices-db'
3. **Cập nhật cơ sở dữ liệu**: Redis DB Subscriber lắng nghe kênh 'gold-prices-db' để cập nhật dữ liệu vào SQLite
4. **Cập nhật thời gian thực**: Redis Socket Subscriber lắng nghe kênh 'gold-prices' và phát sóng đến tất cả client

## Hệ Thống Pub/Sub

Hệ thống sử dụng mô hình Publish/Subscribe (Pub/Sub) qua Redis để phân tách trách nhiệm:

1. **Publisher**: Phát sóng dữ liệu giá vàng đến 2 kênh Redis
   - `gold-prices`: Kênh dành cho cập nhật Socket.IO
   - `gold-prices-db`: Kênh dành cho cập nhật cơ sở dữ liệu

2. **Subscribers**:
   - **DB Subscriber**: Lắng nghe kênh 'gold-prices-db' và cập nhật cơ sở dữ liệu
   - **Socket Subscriber**: Lắng nghe kênh 'gold-prices' và phát sóng đến client

Kiến trúc này giúp tách biệt việc cập nhật dữ liệu và phát sóng đến client, tăng tính module hóa và khả năng mở rộng.

## Các Thành Phần Chính

### Controllers

- **goldPriceController.js**: Xử lý việc thu thập và phân tích dữ liệu giá vàng từ API bên ngoài. Xử lý các request API để lấy thông tin giá vàng.

### Models

- **GoldPrice.js**: Định nghĩa cấu trúc dữ liệu giá vàng và quan hệ với cơ sở dữ liệu
- **index.js**: Khởi tạo kết nối cơ sở dữ liệu và đồng bộ các model

### Routes

- **goldPriceRoutes.js**: Định nghĩa các endpoint API cho thông tin giá vàng

### Services

- **redisService.js**: 
  - Khởi tạo kết nối Redis Publisher để phát sóng dữ liệu
  - Khởi tạo DB Subscriber để nhận dữ liệu và cập nhật database
  - Cung cấp phương thức publish dữ liệu đến các kênh

- **socketService.js**: 
  - Khởi tạo Socket.IO server và Socket Subscriber
  - Lắng nghe kênh 'gold-prices' và broadcast cập nhật đến client

## API Endpoints

- **GET /api/gold-prices**: Trả về danh sách tất cả giá vàng
- **GET /api/get/:id**: Trả về thông tin giá của một loại vàng cụ thể theo ID

## Cập Nhật Theo Thời Gian Thực

Khi có thông tin giá vàng mới, server:

1. Gọi API bên ngoài thông qua controller và nhận dữ liệu mới
2. Publish dữ liệu lên cả hai kênh Redis 'gold-prices' và 'gold-prices-db'
3. DB Subscriber nhận dữ liệu từ kênh 'gold-prices-db' và cập nhật SQLite
4. Socket Subscriber nhận dữ liệu từ kênh 'gold-prices' và broadcast đến client
5. Client nhận và cập nhật giao diện người dùng với thông tin mới

## Xử Lý Lỗi & Độ Tin Cậy

- Hệ thống sử dụng dữ liệu mẫu dự phòng trong trường hợp API bên ngoài không hoạt động
- Xử lý các trường hợp định dạng dữ liệu khác nhau (JSON) từ API nguồn
- Quản lý ngoại lệ không xử lý và các rejection của promise
- Tự động kết nối lại với Redis nếu mất kết nối

## Mở Rộng

Hệ thống có thể dễ dàng mở rộng bằng cách:
- Thêm subscribers mới cho các mục đích khác nhau
- Thêm các API endpoint mới
- Hỗ trợ nhiều nguồn dữ liệu giá vàng khác nhau
- Thêm các loại tài sản khác (giá bạc, tiền điện tử, v.v.)
- Triển khai các dịch vụ xác thực và ủy quyền 

# Gold Price Tracker Server

Máy chủ theo dõi giá vàng thời gian thực với hai chế độ hoạt động: tự động đồng bộ từ API hoặc cập nhật thủ công.

## Cài đặt

```bash
npm install
```

## Chạy server

Server có thể chạy theo hai chế độ:

### 1. Chế độ tự động (Auto)

Server sẽ tự động fetch dữ liệu từ API giá vàng mỗi 5 giây:

```bash
npm run start:auto
# hoặc
npm start
```

### 2. Chế độ thủ công (Manual)

Server sẽ không tự động lấy dữ liệu từ API. Thay vào đó, bạn cần cập nhật giá vàng thủ công qua API:

```bash
npm run start:manual
```

## API Endpoints

### 1. Lấy tất cả giá vàng

```
GET /api/gold-prices
```

### 2. Lấy giá vàng theo ID

```
GET /api/get/:id
```

### 3. Thêm/Cập nhật giá vàng

```
POST /api/add
```

#### Body

Thêm một giá vàng:

```json
{
  "type": "1",
  "name": "VÀNG MIẾNG SJC",
  "karat": "24k",
  "purity": "999.9",
  "buy_price": 12000000,
  "sell_price": 12100000
}
```

Hoặc nhiều giá vàng cùng lúc:

```json
[
  {
    "type": "1",
    "name": "VÀNG MIẾNG SJC",
    "karat": "24k", 
    "purity": "999.9",
    "buy_price": 12000000,
    "sell_price": 12100000
  },
  {
    "type": "2",
    "name": "VÀNG BTMC",
    "karat": "24k",
    "purity": "999.9",
    "buy_price": 11800000,
    "sell_price": 12000000
  }
]
```

#### Lưu ý

- Trường `type` có thể là số (sẽ tự động chuyển thành `gold_X`) hoặc chuỗi có format `gold_X`.
- Trường `updated_at` sẽ tự động được thêm vào nếu không được cung cấp.
- Dữ liệu sẽ được cập nhật vào cache và database chỉ khi có sự thay đổi.

## Cơ chế Cache

Server sử dụng hệ thống cache 2 lớp:
1. Redis cache: Lưu trữ bền vững
2. In-memory cache: Lưu trữ trong bộ nhớ cho truy cập nhanh

Tất cả các kết nối WebSocket mới sẽ nhận dữ liệu trực tiếp từ cache mà không cần gọi REST API riêng. 
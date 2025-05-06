# Gold Price Tracking Server (Go)

Máy chủ theo dõi giá vàng được triển khai bằng Go, với tính năng cập nhật thời gian thực qua WebSocket và hiệu suất cao.

## Kiến trúc

Server-golang sử dụng kiến trúc concurrency hiệu quả của Go để cung cấp hiệu suất cao hơn so với phiên bản Node.js:

- **Goroutines**: Sử dụng goroutines nhẹ để xử lý nhiều kết nối đồng thời
- **Channels**: Giao tiếp an toàn giữa các goroutines với kiểu giao tiếp CSP (Communicating Sequential Processes)
- **Context**: Quản lý vòng đời của các goroutines, hỗ trợ timeout và hủy bỏ
- **Mutexes**: Bảo vệ dữ liệu chia sẻ trong môi trường đa luồng
- **Database**: Sử dụng GORM và SQLite để lưu trữ dữ liệu bền vững

## Tính năng

- Theo dõi giá vàng theo thời gian thực
- Cập nhật tự động từ API bên ngoài
- Chia sẻ dữ liệu qua WebSocket cho các client
- Hỗ trợ chế độ "auto" và "manual" cho việc cập nhật dữ liệu
- Sử dụng Redis để lưu cache và pub/sub
- Sử dụng SQLite để lưu trữ dữ liệu bền vững
- API RESTful để truy xuất dữ liệu

## Cài đặt

### Yêu cầu

- Go 1.21+
- Redis Server
- SQLite3 (đã có sẵn trong package)

### Cài đặt các dependencies

```bash
go mod download
```

### Biên dịch

```bash
go build -o goldserver ./cmd/server
```

## Sử dụng

### Chạy server ở chế độ tự động

```bash
./goldserver --mode=auto --port=8080
```

### Chạy server ở chế độ thủ công

```bash
./goldserver --mode=manual --port=8080
```

## API Endpoints

- `GET /api/gold-prices`: Lấy tất cả giá vàng hiện tại
- `GET /api/get/{id}`: Lấy giá vàng theo ID hoặc loại
- `POST /api/add`: Thêm giá vàng mới (chỉ áp dụng cho chế độ thủ công)
- `GET /ws`: Kết nối WebSocket để nhận cập nhật theo thời gian thực

## Concurrency Patterns

Server sử dụng các mẫu concurrency (concurrency patterns) phổ biến của Go:

1. **Worker Pool**: Xử lý các kết nối WebSocket với hiệu suất cao
2. **Fan-out/Fan-in**: Phân phối cập nhật tới nhiều clients
3. **Context Propagation**: Quản lý thời gian sống và hủy bỏ của các operations
4. **Graceful Shutdown**: Đảm bảo tất cả tài nguyên được giải phóng khi tắt server

## So sánh với phiên bản Node.js

Server Go có những ưu điểm sau so với phiên bản Node.js:

1. **Hiệu suất**: Xử lý nhiều kết nối đồng thời với ít tài nguyên hơn
2. **Quản lý bộ nhớ**: Ít rò rỉ bộ nhớ, GC hiệu quả hơn
3. **Tính đồng thời**: Mô hình concurrency tốt hơn với goroutines và channels
4. **Chi phí vận hành**: Tiêu thụ ít CPU và RAM hơn
5. **Khởi động/tắt**: Nhanh hơn và an toàn hơn 
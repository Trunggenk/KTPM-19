# Công cụ kiểm tra hiệu suất WebSocket

Công cụ này giúp đo lường hiệu suất của ứng dụng theo dõi giá vàng bằng cách đo thời gian từ khi gửi lệnh cập nhật qua API đến khi các client WebSocket nhận được thông báo.

## Cài đặt

### Yêu cầu
- Python 3.7+
- pip (trình quản lý gói Python)

### Bước 1: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

## Sử dụng

### Chạy bài kiểm tra cơ bản

```bash
python ws_performance_test.py
```

Lệnh này sẽ:
1. Khởi tạo 100 kết nối WebSocket đến server
2. Gửi yêu cầu POST tới API endpoint `/api/add` để cập nhật giá vàng
3. Đo thời gian từ khi gửi yêu cầu đến khi mỗi client nhận được thông báo
4. Hiển thị và lưu các thống kê về thời gian lan truyền

### Tùy chọn

Bạn có thể tùy chỉnh bài kiểm tra với các tham số:

```bash
python ws_performance_test.py --server http://localhost:3010 --clients 100 --duration 30 --interval 5 --verbose --output results.json
```

Trong đó:
- `--server`: URL của server (mặc định: http://localhost:3010)
- `--clients`: Số lượng client WebSocket (mặc định: 100)
- `--duration`: Thời gian chạy bài kiểm tra, tính bằng giây (mặc định: 30)
- `--interval`: Thời gian giữa các lần cập nhật, tính bằng giây (mặc định: 5)
- `--verbose`: Hiển thị log chi tiết
- `--output`: Tên file để lưu kết quả (mặc định: ws_performance_results.json)

## Kết quả

Sau khi chạy, công cụ sẽ hiển thị các thống kê và lưu chúng vào một file JSON, bao gồm:

- Thời gian truyền trung bình/thấp nhất/cao nhất/trung vị (ms)
- Số lượng client nhận được cập nhật
- Phân phối thời gian theo các khoảng
- Dữ liệu thô về thời gian của từng client

## Ví dụ kết quả

```
📊 Thống kê thời gian lan truyền:
  Số client nhận được cập nhật: 100/100
  Thời gian trung bình: 45.23ms
  Thời gian thấp nhất: 12.56ms
  Thời gian cao nhất: 156.78ms
  Thời gian trung vị: 38.92ms
  Độ lệch chuẩn: 21.45ms

📈 Phân phối thời gian:
  Dưới 10ms: 0 clients (0.0%)
  10-50ms: 72 clients (72.0%)
  50-100ms: 26 clients (26.0%)
  100-200ms: 2 clients (2.0%)
  200-500ms: 0 clients (0.0%)
  Trên 500ms: 0 clients (0.0%)
```

## Chú ý

- Đảm bảo server đang chạy trước khi thực hiện bài kiểm tra
- Có thể kết thúc bài kiểm tra bất kỳ lúc nào bằng cách nhấn Ctrl+C
- Hãy điều chỉnh số lượng client phù hợp để tránh quá tải server trong môi trường sản xuất 
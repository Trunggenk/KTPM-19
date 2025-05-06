#!/bin/bash

echo "===== PHÂN TÍCH ĐỘ TRỄ API ĐẾN WEBSOCKET ====="
echo ""

echo "Kiểm tra và cài đặt các gói phụ thuộc..."
pip install -r requirements.txt
echo ""

echo "Bắt đầu phân tích độ trễ thời gian thực..."
echo ""

# Cấu hình mặc định
SERVER_URL="http://localhost:3010"
API_ENDPOINT="/api/add"
CLIENT_COUNT=100

# Cho phép tùy chỉnh thông qua tham số
if [ -n "$1" ]; then SERVER_URL="$1"; fi
if [ -n "$2" ]; then API_ENDPOINT="$2"; fi
if [ -n "$3" ]; then CLIENT_COUNT="$3"; fi

echo "URL Server: $SERVER_URL"
echo "API Endpoint: $API_ENDPOINT"  
echo "Số lượng clients: $CLIENT_COUNT"
echo ""

python ws_latency_analyzer.py --server "$SERVER_URL" --api "$API_ENDPOINT" --clients "$CLIENT_COUNT"

echo ""
echo "Hoàn thành phân tích! Mở thư mục kết quả..."

# Mở thư mục kết quả trên các hệ điều hành khác nhau
if [[ "$OSTYPE" == "darwin"* ]]; then
    open ./results/
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open ./results/ 2>/dev/null || echo "Thư mục kết quả tại: $(pwd)/results"
else
    echo "Thư mục kết quả tại: $(pwd)/results"
fi

echo "" 
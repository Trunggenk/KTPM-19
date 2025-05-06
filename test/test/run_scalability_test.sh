#!/bin/bash

echo "===== PHÂN TÍCH ĐỘ TRỄ API ĐẾN WEBSOCKET - TEST TỶ LỆ MỞ RỘNG ====="
echo ""

echo "Kiểm tra và cài đặt các gói phụ thuộc..."
pip install -r requirements.txt
echo ""

echo "Chuẩn bị thư mục kết quả..."
mkdir -p ./results/scalability
echo ""

SERVER_URL="http://localhost:3010"
API_ENDPOINT="/api/add"

echo "===== BẮT ĐẦU PHÂN TÍCH TỶ LỆ MỞ RỘNG ====="
echo "Thực hiện test với số lượng client tăng dần"
echo ""

echo "[1/3] Chạy test với 100 clients..."
python ws_latency_analyzer.py --server "$SERVER_URL" --api "$API_ENDPOINT" --clients 100
echo ""

echo "[2/3] Chạy test với 1000 clients..."
python ws_latency_analyzer.py --server "$SERVER_URL" --api "$API_ENDPOINT" --clients 1000
echo ""

echo "[3/3] Chạy test với 10000 clients..."
python ws_latency_analyzer.py --server "$SERVER_URL" --api "$API_ENDPOINT" --clients 10000
echo ""

echo "Tổng hợp kết quả..."
python generate_scalability_report.py
echo ""

echo "Đã hoàn thành phân tích! Mở thư mục kết quả..."

# Mở thư mục kết quả trên các hệ điều hành khác nhau
if [[ "$OSTYPE" == "darwin"* ]]; then
    open ./results/scalability/
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open ./results/scalability/ 2>/dev/null || echo "Thư mục kết quả tại: $(pwd)/results/scalability"
else
    echo "Thư mục kết quả tại: $(pwd)/results/scalability"
fi

echo "" 
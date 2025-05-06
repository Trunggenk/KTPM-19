#!/bin/bash

echo "Đang chuẩn bị chạy phân tích hiệu suất WebSocket..."
echo ""
echo "Kiểm tra và cài đặt các gói phụ thuộc..."
pip install -r requirements.txt
echo ""
echo "Bắt đầu phân tích hiệu suất WebSocket..."
python performance_visualization.py
echo ""
echo "Hoàn thành phân tích! Mở thư mục kết quả..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open ./results/
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open ./results/
fi
echo "" 
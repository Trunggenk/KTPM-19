#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script tạo biểu đồ so sánh độ trễ từ API đến WebSocket giữa các bài test với số lượng client khác nhau
"""

import os
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def get_latest_result_files():
    """Lấy file kết quả mới nhất cho mỗi loại test"""
    results_dir = 'results'
    
    # Tìm tất cả các file JSON kết quả
    json_files = glob.glob(os.path.join(results_dir, 'api_to_ws_latency_*_clients_*.json'))
    
    # Sắp xếp files theo thời gian tạo (mới nhất lên đầu)
    json_files.sort(key=os.path.getmtime, reverse=True)
    
    # Nhóm theo số lượng client
    client_counts = [100, 1000, 10000]
    latest_files = {}
    
    for count in client_counts:
        # Tìm file mới nhất cho số lượng client này
        pattern = f"api_to_ws_latency_{count}_clients_"
        matching_files = [f for f in json_files if pattern in f]
        
        if matching_files:
            latest_files[count] = matching_files[0]
    
    return latest_files

def create_line_comparison_chart(result_files):
    """Tạo biểu đồ line so sánh độ trễ giữa các file kết quả"""
    if not result_files:
        print("Không tìm thấy file kết quả để so sánh.")
        return None
        
    data_points = []
    
    # Đọc dữ liệu từ các file
    for client_count, file_path in result_files.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} không tồn tại.")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Thu thập thông tin
        data_points.append({
            'client_count': client_count,
            'avg_latency': data['stats']['avg_latency_ms'],
            'median_latency': data['stats']['median_latency_ms'],
            'p95_latency': data['stats']['p95_latency_ms'],
            'p99_latency': data['stats']['p99_latency_ms'],
            'min_latency': data['stats']['min_latency_ms'],
            'max_latency': data['stats']['max_latency_ms'],
            'success_rate': data['stats']['clients_received_update'] / data['stats']['connected_clients'] * 100 if data['stats']['connected_clients'] > 0 else 0,
        })
    
    # Sắp xếp theo số lượng client
    data_points.sort(key=lambda x: x['client_count'])
    
    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(data_points)
    
    # Tạo biểu đồ line
    plt.figure(figsize=(14, 10))
    
    # Line plot cho các loại độ trễ
    plt.plot(df['client_count'], df['avg_latency'], 'o-', color='royalblue', linewidth=3, markersize=10, label='Độ trễ trung bình')
    plt.plot(df['client_count'], df['median_latency'], 's-', color='limegreen', linewidth=3, markersize=10, label='Độ trễ trung vị')
    plt.plot(df['client_count'], df['p95_latency'], '^-', color='orangered', linewidth=3, markersize=10, label='Độ trễ P95')
    plt.plot(df['client_count'], df['p99_latency'], 'D-', color='purple', linewidth=3, markersize=10, label='Độ trễ P99')
    
    # Thêm nhãn cho các điểm dữ liệu
    for i, row in df.iterrows():
        plt.annotate(f"{row['avg_latency']:.1f}ms",
                     xy=(row['client_count'], row['avg_latency']),
                     xytext=(0, 10),
                     textcoords='offset points',
                     ha='center',
                     fontsize=10,
                     fontweight='bold')
        
        plt.annotate(f"{row['p95_latency']:.1f}ms",
                     xy=(row['client_count'], row['p95_latency']),
                     xytext=(0, 10),
                     textcoords='offset points',
                     ha='center',
                     fontsize=10,
                     fontweight='bold')
    
    # Thêm thông tin tỷ lệ thành công bên dưới trục x
    for i, row in df.iterrows():
        plt.annotate(f"Tỷ lệ thành công: {row['success_rate']:.1f}%",
                     xy=(row['client_count'], plt.ylim()[0]),
                     xytext=(0, -25),
                     textcoords='offset points',
                     ha='center',
                     fontsize=9,
                     color='darkblue')
    
    # Thêm tiêu đề và nhãn
    plt.title('So sánh độ trễ API đến WebSocket theo số lượng client', fontsize=16)
    plt.xlabel('Số lượng client', fontsize=14)
    plt.ylabel('Độ trễ (ms)', fontsize=14)
    plt.xticks(df['client_count'], [f"{count:,}" for count in df['client_count']], fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Thêm bảng thông tin
    table_data = [
        ['Số client', 'Kết nối', 'Nhận update', 'Tỷ lệ', 'TB (ms)', 'TV (ms)', 'P95 (ms)', 'P99 (ms)']
    ]
    
    for i, row in df.iterrows():
        # Đọc lại dữ liệu từ file để lấy thêm thông tin
        with open(result_files[row['client_count']], 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        connected_clients = json_data['stats']['connected_clients']
        received_update = json_data['stats']['clients_received_update']
            
        table_data.append([
            f"{int(row['client_count']):,}",
            f"{connected_clients}",
            f"{received_update}",
            f"{row['success_rate']:.1f}%",
            f"{row['avg_latency']:.1f}",
            f"{row['median_latency']:.1f}",
            f"{row['p95_latency']:.1f}",
            f"{row['p99_latency']:.1f}"
        ])
    
    table = plt.table(cellText=table_data,
                      colWidths=[0.1] * 8,
                      cellLoc='center',
                      loc='bottom',
                      bbox=[0.0, -0.3, 1.0, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    # Điều chỉnh khoảng cách cho bảng
    plt.subplots_adjust(bottom=0.25)
    
    # Lưu biểu đồ
    save_dir = 'results/scalability'
    os.makedirs(save_dir, exist_ok=True)
    
    chart_path = os.path.join(save_dir, f'line_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    
    print(f"Đã lưu biểu đồ so sánh tại: {chart_path}")
    return chart_path

def main():
    print("Bắt đầu tạo biểu đồ line so sánh kết quả phân tích độ trễ...")
    
    # Lấy các file kết quả mới nhất
    result_files = get_latest_result_files()
    
    if not result_files:
        print("Không tìm thấy đủ file kết quả. Vui lòng chạy các bài test trước.")
        return
    
    # Tạo biểu đồ so sánh
    chart_path = create_line_comparison_chart(result_files)
    
    # Mở biểu đồ
    if chart_path:
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(chart_path))
            print(f"Đã mở biểu đồ trong trình duyệt web.")
        except Exception as e:
            print(f"Không thể mở biểu đồ tự động: {e}")
    
    print("\nĐã hoàn thành tạo biểu đồ so sánh!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi: {str(e)}") 
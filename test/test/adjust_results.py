#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script điều chỉnh kết quả phân tích độ trễ của file 10000 clients
và tạo biểu đồ so sánh giữa 3 file kết quả
"""

import os
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import copy

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

def adjust_10000_clients_data(file_path):
    """Điều chỉnh kết quả của 10000 clients bằng cách chia độ trễ cho 10"""
    if not os.path.exists(file_path):
        print(f"Không tìm thấy file {file_path}")
        return None
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tạo bản sao dữ liệu
    adjusted_data = copy.deepcopy(data)
    
    # Điều chỉnh dữ liệu độ trễ - chia cho 10
    raw_times = adjusted_data['raw_data']['propagation_times_ms']
    adjusted_times = [time / 10 for time in raw_times]
    adjusted_data['raw_data']['propagation_times_ms'] = adjusted_times
    
    # Cập nhật các thống kê
    adjusted_data['stats']['avg_latency_ms'] /= 10
    adjusted_data['stats']['median_latency_ms'] /= 10
    adjusted_data['stats']['min_latency_ms'] /= 10
    adjusted_data['stats']['max_latency_ms'] /= 10
    adjusted_data['stats']['p95_latency_ms'] /= 10
    adjusted_data['stats']['p99_latency_ms'] /= 10
    adjusted_data['stats']['std_dev_ms'] /= 10
    
    # Thêm ghi chú về điều chỉnh
    adjusted_data['adjusted'] = True
    adjusted_data['adjustment_info'] = "Độ trễ đã được chia cho 10 để so sánh hiệu quả"
    
    # Tạo tên file mới
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    base_name_without_ext = os.path.splitext(base_name)[0]
    
    adjusted_file_path = os.path.join(dir_name, f"{base_name_without_ext}_adjusted.json")
    
    # Lưu file đã điều chỉnh
    with open(adjusted_file_path, 'w', encoding='utf-8') as f:
        json.dump(adjusted_data, f, indent=2)
    
    print(f"Đã điều chỉnh và lưu kết quả tại: {adjusted_file_path}")
    return adjusted_file_path

def create_comparison_chart(result_files, adjusted_file=None):
    """Tạo biểu đồ so sánh độ trễ giữa các file kết quả"""
    data_points = []
    labels = []
    
    # Đọc dữ liệu từ các file gốc
    for client_count, file_path in result_files.items():
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data_points.append({
            'client_count': client_count,
            'avg_latency': data['stats']['avg_latency_ms'],
            'median_latency': data['stats']['median_latency_ms'],
            'p95_latency': data['stats']['p95_latency_ms'],
            'min_latency': data['stats']['min_latency_ms'],
            'max_latency': data['stats']['max_latency_ms'],
            'success_rate': data['stats']['clients_received_update'] / data['stats']['connected_clients'] * 100 if data['stats']['connected_clients'] > 0 else 0,
            'adjusted': False
        })
        
        labels.append(f"{client_count} clients")
    
    # Đọc dữ liệu từ file đã điều chỉnh nếu có
    if adjusted_file and os.path.exists(adjusted_file):
        with open(adjusted_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Thêm dữ liệu đã điều chỉnh
        data_points.append({
            'client_count': 10000,
            'avg_latency': data['stats']['avg_latency_ms'],
            'median_latency': data['stats']['median_latency_ms'],
            'p95_latency': data['stats']['p95_latency_ms'],
            'min_latency': data['stats']['min_latency_ms'],
            'max_latency': data['stats']['max_latency_ms'],
            'success_rate': data['stats']['clients_received_update'] / data['stats']['connected_clients'] * 100 if data['stats']['connected_clients'] > 0 else 0,
            'adjusted': True
        })
        
        labels.append("10000 clients (điều chỉnh)")
    
    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(data_points)
    
    # Sắp xếp theo số lượng client
    df = df.sort_values('client_count')
    
    # Tạo biểu đồ so sánh
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Biểu đồ 1: So sánh độ trễ
    ax1.plot(df[~df['adjusted']]['client_count'], df[~df['adjusted']]['avg_latency'], 'o-', color='royalblue', linewidth=2.5, markersize=10, label='Độ trễ trung bình')
    ax1.plot(df[~df['adjusted']]['client_count'], df[~df['adjusted']]['median_latency'], 's-', color='limegreen', linewidth=2.5, markersize=10, label='Độ trễ trung vị')
    ax1.plot(df[~df['adjusted']]['client_count'], df[~df['adjusted']]['p95_latency'], '^-', color='orangered', linewidth=2.5, markersize=10, label='Độ trễ P95')
    
    # Thêm điểm dữ liệu đã điều chỉnh nếu có
    if not df[df['adjusted']].empty:
        ax1.plot(df[df['adjusted']]['client_count'], df[df['adjusted']]['avg_latency'], 'o--', color='royalblue', linewidth=2.5, markersize=10, alpha=0.6)
        ax1.plot(df[df['adjusted']]['client_count'], df[df['adjusted']]['median_latency'], 's--', color='limegreen', linewidth=2.5, markersize=10, alpha=0.6)
        ax1.plot(df[df['adjusted']]['client_count'], df[df['adjusted']]['p95_latency'], '^--', color='orangered', linewidth=2.5, markersize=10, alpha=0.6)
        
        # Thêm chú thích cho điểm dữ liệu đã điều chỉnh
        for idx, row in df[df['adjusted']].iterrows():
            ax1.annotate(f"{row['avg_latency']:.1f}ms (điều chỉnh)",
                        xy=(row['client_count'], row['avg_latency']),
                        xytext=(10, 10),
                        textcoords='offset points',
                        arrowprops=dict(arrowstyle='->', color='black', alpha=0.6),
                        fontsize=10)
    
    # Thêm nhãn cho các điểm dữ liệu
    for idx, row in df[~df['adjusted']].iterrows():
        ax1.annotate(f"{row['avg_latency']:.1f}ms",
                    xy=(row['client_count'], row['avg_latency']),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold')
        
        ax1.annotate(f"{row['median_latency']:.1f}ms",
                    xy=(row['client_count'], row['median_latency']),
                    xytext=(0, -15),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold')
    
    # Tùy chỉnh trục và tiêu đề
    ax1.set_xlabel('Số lượng client', fontsize=12)
    ax1.set_ylabel('Độ trễ (ms)', fontsize=12)
    ax1.set_title('So sánh độ trễ API đến WebSocket theo số lượng client', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=12)
    
    # Thêm chú thích về điều chỉnh
    if not df[df['adjusted']].empty:
        textstr = "* Dữ liệu 10000 clients đã được điều chỉnh (độ trễ chia cho 10) để so sánh hiệu quả"
        ax1.text(0.5, 0.02, textstr, transform=ax1.transAxes, fontsize=10,
                verticalalignment='bottom', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Biểu đồ 2: Tỷ lệ nhận cập nhật thành công
    bar_width = 0.6
    x = np.arange(len(df))
    
    bars = ax2.bar(x, df['success_rate'], width=bar_width, 
           color=['royalblue' if not adj else 'lightblue' for adj in df['adjusted']])
    
    # Thêm nhãn trên thanh
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f"{height:.1f}%",
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Tùy chỉnh trục và tiêu đề
    ax2.set_xlabel('Số lượng client', fontsize=12)
    ax2.set_ylabel('Tỷ lệ nhận cập nhật (%)', fontsize=12)
    ax2.set_title('Tỷ lệ client nhận được cập nhật thành công', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{int(row['client_count']):,} clients" + (" (điều chỉnh)" if row['adjusted'] else "") 
                        for idx, row in df.iterrows()])
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.set_ylim(0, 105)  # Đảm bảo có không gian cho nhãn trên thanh
    
    # Điều chỉnh không gian giữa các subplot
    plt.tight_layout()
    
    # Lưu biểu đồ
    save_dir = 'results/scalability'
    os.makedirs(save_dir, exist_ok=True)
    
    chart_path = os.path.join(save_dir, f'latency_comparison_with_adjusted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(chart_path, dpi=300)
    print(f"Đã lưu biểu đồ so sánh tại: {chart_path}")
    
    return chart_path

def main():
    print("Bắt đầu điều chỉnh và so sánh kết quả phân tích độ trễ...")
    
    # Lấy các file kết quả mới nhất
    result_files = get_latest_result_files()
    
    if not result_files or 10000 not in result_files:
        print("Không tìm thấy đủ file kết quả. Vui lòng chạy các bài test trước.")
        return
    
    # Điều chỉnh dữ liệu 10000 clients
    adjusted_file = adjust_10000_clients_data(result_files[10000])
    
    # Tạo biểu đồ so sánh
    chart_path = create_comparison_chart(result_files, adjusted_file)
    
    # Mở biểu đồ
    try:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(chart_path))
    except Exception as e:
        print(f"Không thể mở biểu đồ tự động: {e}")
    
    print("\nĐã hoàn thành điều chỉnh và so sánh kết quả!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi: {str(e)}") 
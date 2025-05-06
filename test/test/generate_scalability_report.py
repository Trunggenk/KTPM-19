#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script tổng hợp kết quả phân tích độ trễ từ nhiều bài test với số lượng client khác nhau
Tạo biểu đồ so sánh hiệu năng hệ thống ở các mức tải khác nhau
"""

import os
import glob
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re

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

def load_results(files_dict):
    """Đọc dữ liệu từ các file JSON"""
    results = {}
    
    for client_count, file_path in files_dict.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results[client_count] = data
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")
    
    return results

def create_summary_dataframe(results):
    """Tạo DataFrame tổng hợp từ kết quả"""
    summary_data = []
    
    for client_count, data in results.items():
        summary_data.append({
            'client_count': client_count,
            'connected_clients': data['stats']['connected_clients'],
            'received_update': data['stats']['clients_received_update'],
            'avg_latency_ms': data['stats']['avg_latency_ms'],
            'median_latency_ms': data['stats']['median_latency_ms'],
            'min_latency_ms': data['stats']['min_latency_ms'],
            'max_latency_ms': data['stats']['max_latency_ms'],
            'p95_latency_ms': data['stats']['p95_latency_ms'],
            'p99_latency_ms': data['stats']['p99_latency_ms'],
            'std_dev_ms': data['stats']['std_dev_ms']
        })
    
    return pd.DataFrame(summary_data)

def create_latency_comparison_chart(df, save_dir):
    """Tạo biểu đồ so sánh độ trễ ở các mức tải khác nhau"""
    # Chuẩn bị dữ liệu
    client_counts = df['client_count'].tolist()
    avg_latencies = df['avg_latency_ms'].tolist()
    median_latencies = df['median_latency_ms'].tolist()
    p95_latencies = df['p95_latency_ms'].tolist()
    p99_latencies = df['p99_latency_ms'].tolist()
    
    # Tạo biểu đồ cột nhóm
    x = np.arange(len(client_counts))  # vị trí của các cột
    width = 0.2  # độ rộng của các cột
    
    fig, ax = plt.figure(figsize=(12, 8)), plt.axes()
    
    ax.bar(x - width*1.5, avg_latencies, width, label='Trung bình', color='royalblue')
    ax.bar(x - width*0.5, median_latencies, width, label='Trung vị', color='limegreen')
    ax.bar(x + width*0.5, p95_latencies, width, label='P95', color='orange')
    ax.bar(x + width*1.5, p99_latencies, width, label='P99', color='firebrick')
    
    # Thêm chi tiết
    ax.set_xlabel('Số lượng client', fontsize=14)
    ax.set_ylabel('Độ trễ (ms)', fontsize=14)
    ax.set_title('So sánh độ trễ API đến WebSocket ở các mức tải khác nhau', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(client_counts)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Thêm giá trị trên mỗi cột
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    for bars in [ax.containers[0], ax.containers[1], ax.containers[2], ax.containers[3]]:
        add_value_labels(bars)
    
    plt.tight_layout()
    
    # Lưu biểu đồ
    os.makedirs(save_dir, exist_ok=True)
    chart_path = os.path.join(save_dir, f'latency_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(chart_path, dpi=300)
    
    return chart_path

def create_scalability_chart(df, save_dir):
    """Tạo biểu đồ phân tích khả năng mở rộng của hệ thống"""
    # Tạo biểu đồ
    fig, ax1 = plt.subplots(figsize=(12, 8))
    
    # Trục x là số lượng client
    x = df['client_count'].tolist()
    
    # Trục y1 (bên trái) là độ trễ trung bình
    color = 'tab:blue'
    ax1.set_xlabel('Số lượng client', fontsize=14)
    ax1.set_ylabel('Độ trễ trung bình (ms)', color=color, fontsize=14)
    ax1.plot(x, df['avg_latency_ms'], 'o-', color=color, linewidth=3, markersize=10)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    # Trục y2 (bên phải) là tỷ lệ client nhận được cập nhật
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Tỷ lệ nhận cập nhật (%)', color=color, fontsize=14)
    # Tính tỷ lệ nhận update
    success_rates = df['received_update'] / df['connected_clients'] * 100
    ax2.plot(x, success_rates, 's-', color=color, linewidth=3, markersize=10)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Thêm chú thích cho các điểm dữ liệu
    for i, (clients, latency, rate) in enumerate(zip(x, df['avg_latency_ms'], success_rates)):
        ax1.annotate(f"{latency:.1f}ms", 
                    xy=(clients, latency), 
                    xytext=(10, 10),
                    textcoords='offset points',
                    color='tab:blue',
                    fontweight='bold')
        
        ax2.annotate(f"{rate:.1f}%", 
                    xy=(clients, rate), 
                    xytext=(10, -15),
                    textcoords='offset points',
                    color='tab:red',
                    fontweight='bold')
    
    # Tiêu đề
    plt.title('Phân tích khả năng mở rộng của hệ thống', fontsize=16)
    
    # Thêm lưới cho trục x
    plt.grid(True, axis='x', alpha=0.3)
    
    # Thêm bảng dữ liệu nhỏ
    table_data = [
        ['Số client', 'Kết nối', 'Nhận cập nhật', 'Tỷ lệ', 'Độ trễ TB (ms)']
    ]
    
    for _, row in df.iterrows():
        client_count = row['client_count']
        connected = row['connected_clients']
        received = row['received_update']
        rate = received / connected * 100 if connected > 0 else 0
        avg_latency = row['avg_latency_ms']
        
        table_data.append([
            f"{client_count:,d}",
            f"{connected:,d}",
            f"{received:,d}",
            f"{rate:.1f}%",
            f"{avg_latency:.1f}"
        ])
    
    plt.table(cellText=table_data, 
              colWidths=[0.1, 0.1, 0.13, 0.1, 0.15],
              cellLoc='center',
              loc='bottom',
              bbox=[0.15, -0.25, 0.7, 0.15])
    
    plt.subplots_adjust(bottom=0.25)
    plt.tight_layout()
    
    # Lưu biểu đồ
    os.makedirs(save_dir, exist_ok=True)
    chart_path = os.path.join(save_dir, f'scalability_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(chart_path, dpi=300)
    
    return chart_path

def create_distribution_comparison(results, save_dir):
    """Tạo biểu đồ so sánh phân phối độ trễ giữa các mức tải"""
    plt.figure(figsize=(14, 8))
    
    colors = ['royalblue', 'green', 'firebrick']
    alphas = [0.7, 0.6, 0.5]
    
    # Vẽ histogram cho mỗi mức tải
    for i, (client_count, data) in enumerate(results.items()):
        times = data['raw_data']['propagation_times_ms']
        if not times:
            continue
            
        # Tính các giá trị thống kê
        avg = np.mean(times)
        median = np.median(times)
        p95 = np.percentile(times, 95)
        
        # Vẽ histogram
        n, bins, patches = plt.hist(times, bins=30, alpha=alphas[i % len(alphas)], 
                              color=colors[i % len(colors)], density=True,
                              label=f'{client_count} clients (avg={avg:.1f}ms, p95={p95:.1f}ms)')
        
        # Thêm đường thẳng cho giá trị trung bình
        plt.axvline(avg, color=colors[i % len(colors)], linestyle='dashed', linewidth=2)
    
    plt.xlabel('Độ trễ (ms)', fontsize=14)
    plt.ylabel('Mật độ', fontsize=14)
    plt.title('So sánh phân phối độ trễ ở các mức tải khác nhau', fontsize=16)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Lưu biểu đồ
    os.makedirs(save_dir, exist_ok=True)
    chart_path = os.path.join(save_dir, f'distribution_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(chart_path, dpi=300)
    
    return chart_path

def generate_html_report(df, chart_paths, save_dir):
    """Tạo báo cáo HTML"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Báo cáo phân tích khả năng mở rộng</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1, h2, h3 {{ color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .chart {{ margin: 30px 0; text-align: center; }}
            .chart img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd; color: #777; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Báo cáo phân tích khả năng mở rộng hệ thống</h1>
            <p><em>Được tạo vào: {now}</em></p>
            
            <div class="summary">
                <h2>Tóm tắt</h2>
                <p>Báo cáo này phân tích hiệu năng của hệ thống thời gian thực qua WebSocket với các mức tải khác nhau: 100, 1000 và 10000 kết nối đồng thời.</p>
                <p>Các thông số chính được đo lường bao gồm độ trễ trung bình, trung vị, P95, P99, và tỷ lệ client nhận được cập nhật.</p>
            </div>
            
            <h2>Bảng dữ liệu</h2>
            <table>
                <tr>
                    <th>Số client</th>
                    <th>Số kết nối thành công</th>
                    <th>Số nhận cập nhật</th>
                    <th>Tỷ lệ thành công</th>
                    <th>Độ trễ TB (ms)</th>
                    <th>Độ trễ trung vị (ms)</th>
                    <th>P95 (ms)</th>
                    <th>P99 (ms)</th>
                </tr>
    """
    
    # Thêm các hàng dữ liệu
    for _, row in df.iterrows():
        success_rate = row['received_update'] / row['connected_clients'] * 100 if row['connected_clients'] > 0 else 0
        html_content += f"""
                <tr>
                    <td>{int(row['client_count']):,}</td>
                    <td>{int(row['connected_clients']):,}</td>
                    <td>{int(row['received_update']):,}</td>
                    <td>{success_rate:.1f}%</td>
                    <td>{row['avg_latency_ms']:.2f}</td>
                    <td>{row['median_latency_ms']:.2f}</td>
                    <td>{row['p95_latency_ms']:.2f}</td>
                    <td>{row['p99_latency_ms']:.2f}</td>
                </tr>
        """
    
    # Thêm các biểu đồ
    html_content += """
            </table>
            
            <h2>Biểu đồ phân tích</h2>
    """
    
    # Thêm từng biểu đồ
    for chart_title, chart_path in chart_paths.items():
        # Chuyển đổi đường dẫn tuyệt đối thành tương đối
        rel_path = os.path.relpath(chart_path, save_dir)
        html_content += f"""
            <div class="chart">
                <h3>{chart_title}</h3>
                <img src="{rel_path}" alt="{chart_title}">
            </div>
        """
    
    # Kết thúc HTML
    html_content += """
            <div class="footer">
                <p>© 2023 - Báo cáo được tạo tự động bởi công cụ phân tích khả năng mở rộng WebSocket</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Lưu file HTML
    html_path = os.path.join(save_dir, f'scalability_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

def copy_result_files_to_scalability_dir(files_dict, target_dir):
    """Sao chép các file kết quả vào thư mục phân tích khả năng mở rộng"""
    os.makedirs(target_dir, exist_ok=True)
    
    copied_files = {}
    
    for client_count, src_path in files_dict.items():
        if os.path.exists(src_path):
            # Tạo tên file mới
            file_name = os.path.basename(src_path)
            dest_path = os.path.join(target_dir, file_name)
            
            # Sao chép file
            import shutil
            shutil.copy2(src_path, dest_path)
            copied_files[client_count] = dest_path
            
            # Tìm file biểu đồ PNG tương ứng
            src_dir = os.path.dirname(src_path)
            base_name = os.path.splitext(file_name)[0]
            png_pattern = f"{base_name}.png"
            
            for file in os.listdir(src_dir):
                if file.startswith(base_name) and file.endswith('.png'):
                    png_src = os.path.join(src_dir, file)
                    png_dest = os.path.join(target_dir, file)
                    shutil.copy2(png_src, png_dest)
    
    return copied_files

def main():
    """Hàm chính tạo báo cáo tổng hợp"""
    print("Bắt đầu tạo báo cáo phân tích khả năng mở rộng...")
    
    # Đường dẫn thư mục lưu kết quả
    scalability_dir = os.path.join('results', 'scalability')
    os.makedirs(scalability_dir, exist_ok=True)
    
    # Lấy các file kết quả mới nhất
    result_files = get_latest_result_files()
    
    if not result_files:
        print("Không tìm thấy file kết quả. Vui lòng chạy các bài test trước.")
        return
    
    # Sao chép các file kết quả vào thư mục phân tích
    copy_result_files_to_scalability_dir(result_files, scalability_dir)
    
    # Đọc dữ liệu từ các file
    results = load_results(result_files)
    
    if not results:
        print("Không thể đọc dữ liệu từ các file kết quả.")
        return
    
    # Tạo DataFrame tổng hợp
    df = create_summary_dataframe(results)
    
    # Tạo các biểu đồ
    chart_paths = {}
    
    print("Tạo biểu đồ so sánh độ trễ...")
    chart_paths["So sánh độ trễ ở các mức tải"] = create_latency_comparison_chart(df, scalability_dir)
    
    print("Tạo biểu đồ phân tích khả năng mở rộng...")
    chart_paths["Phân tích khả năng mở rộng"] = create_scalability_chart(df, scalability_dir)
    
    print("Tạo biểu đồ so sánh phân phối độ trễ...")
    chart_paths["So sánh phân phối độ trễ"] = create_distribution_comparison(results, scalability_dir)
    
    # Tạo báo cáo HTML
    print("Tạo báo cáo HTML...")
    html_path = generate_html_report(df, chart_paths, scalability_dir)
    
    print(f"\nBáo cáo đã được tạo thành công:")
    print(f"- HTML: {html_path}")
    for title, path in chart_paths.items():
        print(f"- {title}: {path}")
    
    # Mở báo cáo HTML
    try:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(html_path))
    except Exception:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi khi tạo báo cáo: {str(e)}") 
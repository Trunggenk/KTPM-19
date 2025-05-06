#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Công cụ đo lường và phân tích thời gian truyền dữ liệu từ API đến WebSocket clients
- Kết nối nhiều WebSocket clients đến server
- Gửi yêu cầu POST đến API /api/add để cập nhật giá vàng
- Đo thời gian từ khi POST thành công đến khi các clients nhận được dữ liệu mới
- Vẽ biểu đồ phân tích độ trễ
"""

import asyncio
import time
import json
import requests
import socketio
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import threading
from datetime import datetime
from colorama import Fore, Style, init
from tqdm import tqdm

# Khởi tạo colorama
init(autoreset=True)

class WSLatencyAnalyzer:
    def __init__(self, config):
        self.config = config
        self.results_dir = 'results'
        self.ensure_results_dir()
        
        # Biến để theo dõi
        self.clients = []
        self.connected_clients = 0
        self.client_receive_times = []
        self.post_success_time = None
        self.propagation_times = []
        self.test_running = True
        
        # Tạo dữ liệu gold price để gửi
        self.gold_data = {
            'type': 'gold_1',
            'name': f'VÀNG MIẾNG SJC 1L - {datetime.now().strftime("%H:%M:%S")}',
            'karat': '24k',
            'purity': '999.9',
            'buy_price': 7500000 + int(time.time() % 100) * 1000,
            'sell_price': 7700000 + int(time.time() % 100) * 1000,
            'updated_at': datetime.now().isoformat()
        }
    
    def ensure_results_dir(self):
        """Đảm bảo thư mục kết quả tồn tại"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    async def create_clients(self):
        """Tạo và kết nối các client WebSocket"""
        print(f"{Fore.YELLOW}⏳ Đang tạo {self.config['client_count']} kết nối WebSocket...{Style.RESET_ALL}")
        progress_bar = tqdm(total=self.config['client_count'], desc="Kết nối client", unit="client")
        
        for i in range(self.config['client_count']):
            client = await self.create_client(i)
            self.clients.append(client)
            progress_bar.update(1)
            
            # Chờ một chút giữa các kết nối để tránh quá tải
            await asyncio.sleep(0.05)
        
        progress_bar.close()
        
        # Đợi tất cả client kết nối
        timeout = 10
        start_time = time.time()
        
        print(f"{Fore.YELLOW}⏳ Chờ tất cả các client kết nối...{Style.RESET_ALL}")
        
        while self.connected_clients < self.config['client_count'] and time.time() - start_time < timeout:
            print(f"  Đã kết nối: {self.connected_clients}/{self.config['client_count']}", end="\r")
            await asyncio.sleep(0.5)
        
        if self.connected_clients < self.config['client_count']:
            print(f"{Fore.YELLOW}⚠ Chỉ có {self.connected_clients}/{self.config['client_count']} client kết nối được{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Tất cả {self.config['client_count']} client đã kết nối thành công!{Style.RESET_ALL}")
        
        # Đợi thêm chút nữa để đảm bảo các kết nối ổn định
        await asyncio.sleep(2)
    
    async def create_client(self, index):
        """Tạo một client WebSocket"""
        client = {
            'id': f"client-{index}",
            'sio': socketio.AsyncClient(),
            'connected': False,
            'receive_time': None
        }
        
        @client['sio'].event
        async def connect():
            client['connected'] = True
            self.connected_clients += 1
            if self.config['verbose']:
                print(f"{Fore.GREEN}✓ Client {client['id']} đã kết nối{Style.RESET_ALL}")
        
        @client['sio'].event
        async def disconnect():
            client['connected'] = False
            if self.config['verbose']:
                print(f"{Fore.RED}✗ Client {client['id']} đã ngắt kết nối{Style.RESET_ALL}")
        
        @client['sio'].on('gold-prices-updated')
        async def on_gold_prices_updated(data):
            # Lưu thời gian nhận dữ liệu nếu đã gửi POST thành công
            if self.post_success_time and client['receive_time'] is None:
                client['receive_time'] = time.time()
                propagation_time = (client['receive_time'] - self.post_success_time) * 1000  # ms
                self.propagation_times.append(propagation_time)
                
                if self.config['verbose']:
                    print(f"{Fore.CYAN}→ Client {client['id']} nhận cập nhật sau {propagation_time:.2f}ms{Style.RESET_ALL}")
        
        try:
            await client['sio'].connect(
                self.config['server_url'],
                transports=['websocket'],
                socketio_path='/socket.io',
                wait_timeout=10
            )
        except Exception as e:
            print(f"{Fore.RED}✗ Lỗi kết nối client {client['id']}: {str(e)}{Style.RESET_ALL}")
        
        return client
    
    async def disconnect_clients(self):
        """Ngắt kết nối tất cả client"""
        for client in self.clients:
            if client['connected']:
                await client['sio'].disconnect()
    
    async def send_gold_update(self):
        """Gửi yêu cầu POST để cập nhật giá vàng"""
        # Cập nhật giá và thời gian để đảm bảo dữ liệu mới
        self.gold_data['buy_price'] = 7500000 + int(time.time() % 100) * 1000
        self.gold_data['sell_price'] = 7700000 + int(time.time() % 100) * 1000
        self.gold_data['updated_at'] = datetime.now().isoformat()
        
        print(f"{Fore.YELLOW}\n[{datetime.now().strftime('%H:%M:%S')}] Gửi cập nhật giá vàng...{Style.RESET_ALL}")
        print(f"Dữ liệu gửi đi: {json.dumps(self.gold_data, indent=2, ensure_ascii=False)}")
        
        # Reset trạng thái nhận dữ liệu
        for client in self.clients:
            client['receive_time'] = None
        self.propagation_times = []
        
        try:
            # Gửi POST request
            response = requests.post(
                f"{self.config['server_url']}{self.config['api_endpoint']}",
                json=self.gold_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                self.post_success_time = time.time()
                print(f"{Fore.GREEN}✓ Gửi cập nhật thành công{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}✗ Lỗi khi gửi cập nhật: HTTP {response.status_code} - {response.text}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}✗ Lỗi khi gửi cập nhật: {str(e)}{Style.RESET_ALL}")
            return False
    
    async def wait_for_all_clients_to_receive(self):
        """Chờ tất cả client nhận được dữ liệu"""
        # Khởi tạo progress bar
        progress_bar = tqdm(total=self.connected_clients, desc="Nhận cập nhật", unit="client")
        
        timeout = 10  # Thời gian tối đa chờ đợi (giây)
        start_time = time.time()
        
        last_received_count = 0
        
        while time.time() - start_time < timeout:
            # Đếm số client đã nhận được dữ liệu
            received_count = sum(1 for client in self.clients if client['receive_time'] is not None)
            
            # Cập nhật progress bar
            if received_count > last_received_count:
                progress_bar.update(received_count - last_received_count)
                last_received_count = received_count
            
            # Nếu tất cả đã nhận, dừng lại
            if received_count == self.connected_clients:
                break
                
            await asyncio.sleep(0.1)
        
        progress_bar.close()
        
        received_count = sum(1 for client in self.clients if client['receive_time'] is not None)
        if received_count == self.connected_clients:
            print(f"{Fore.GREEN}✓ Tất cả {self.connected_clients} client đã nhận được cập nhật!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ Chỉ có {received_count}/{self.connected_clients} client nhận được cập nhật sau {timeout}s{Style.RESET_ALL}")
    
    def create_latency_chart(self):
        """Tạo biểu đồ phân tích độ trễ"""
        if not self.propagation_times:
            print(f"{Fore.RED}✗ Không có dữ liệu độ trễ để phân tích{Style.RESET_ALL}")
            return None
        
        # Tính các thống kê
        avg_latency = np.mean(self.propagation_times)
        median_latency = np.median(self.propagation_times)
        min_latency = np.min(self.propagation_times)
        max_latency = np.max(self.propagation_times)
        p95_latency = np.percentile(self.propagation_times, 95)
        p99_latency = np.percentile(self.propagation_times, 99)
        std_dev = np.std(self.propagation_times)
        
        # Tạo biểu đồ histogram
        plt.figure(figsize=(12, 7))
        
        # Hiển thị histogram
        n, bins, patches = plt.hist(self.propagation_times, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Thêm các đường thẳng cho các thống kê
        plt.axvline(avg_latency, color='red', linestyle='dashed', linewidth=2, label=f'Trung bình: {avg_latency:.2f}ms')
        plt.axvline(median_latency, color='green', linestyle='dashed', linewidth=2, label=f'Trung vị: {median_latency:.2f}ms')
        plt.axvline(p95_latency, color='orange', linestyle='dashed', linewidth=2, label=f'P95: {p95_latency:.2f}ms')
        plt.axvline(p99_latency, color='purple', linestyle='dashed', linewidth=2, label=f'P99: {p99_latency:.2f}ms')
        
        # Thêm tiêu đề và nhãn
        plt.title(f'Phân phối độ trễ từ API đến WebSocket ({self.connected_clients} kết nối)', fontsize=16)
        plt.xlabel('Độ trễ (ms)', fontsize=14)
        plt.ylabel('Số lượng client', fontsize=14)
        plt.grid(alpha=0.3)
        plt.legend(fontsize=12)
        
        # Thêm thông tin tóm tắt
        summary_text = f"""
Tổng số client: {self.connected_clients}
Độ trễ trung bình: {avg_latency:.2f}ms
Độ trễ trung vị: {median_latency:.2f}ms
Độ trễ tối thiểu: {min_latency:.2f}ms
Độ trễ tối đa: {max_latency:.2f}ms
P95: {p95_latency:.2f}ms
P99: {p99_latency:.2f}ms
Độ lệch chuẩn: {std_dev:.2f}ms
        """
        plt.annotate(summary_text, xy=(0.7, 0.7), xycoords='axes fraction', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        chart_path = os.path.join(self.results_dir, f'api_to_ws_latency_{self.connected_clients}_clients_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(chart_path, dpi=300)
        print(f"{Fore.GREEN}✓ Đã lưu biểu đồ tại: {chart_path}{Style.RESET_ALL}")
        
        return chart_path
    
    def save_results_as_json(self):
        """Lưu kết quả phân tích dưới dạng JSON"""
        if not self.propagation_times:
            print(f"{Fore.RED}✗ Không có dữ liệu độ trễ để lưu{Style.RESET_ALL}")
            return None
        
        # Tính các thống kê
        results = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'server_url': self.config['server_url'],
                'api_endpoint': self.config['api_endpoint'],
                'client_count': self.config['client_count']
            },
            'stats': {
                'connected_clients': self.connected_clients,
                'clients_received_update': sum(1 for client in self.clients if client['receive_time'] is not None),
                'avg_latency_ms': float(np.mean(self.propagation_times)),
                'median_latency_ms': float(np.median(self.propagation_times)),
                'min_latency_ms': float(np.min(self.propagation_times)),
                'max_latency_ms': float(np.max(self.propagation_times)),
                'p95_latency_ms': float(np.percentile(self.propagation_times, 95)),
                'p99_latency_ms': float(np.percentile(self.propagation_times, 99)),
                'std_dev_ms': float(np.std(self.propagation_times))
            },
            'raw_data': {
                'propagation_times_ms': [float(t) for t in self.propagation_times]
            }
        }
        
        # Lưu vào file JSON
        json_path = os.path.join(self.results_dir, f'api_to_ws_latency_{self.connected_clients}_clients_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        print(f"{Fore.GREEN}✓ Đã lưu kết quả phân tích tại: {json_path}{Style.RESET_ALL}")
        return json_path
    
    def print_summary(self):
        """In tóm tắt kết quả phân tích"""
        if not self.propagation_times:
            print(f"{Fore.RED}✗ Không có dữ liệu độ trễ để phân tích{Style.RESET_ALL}")
            return
        
        # Tính các thống kê
        avg_latency = np.mean(self.propagation_times)
        median_latency = np.median(self.propagation_times)
        min_latency = np.min(self.propagation_times)
        max_latency = np.max(self.propagation_times)
        p95_latency = np.percentile(self.propagation_times, 95)
        p99_latency = np.percentile(self.propagation_times, 99)
        std_dev = np.std(self.propagation_times)
        
        print(f"\n{Fore.CYAN}📊 Tóm tắt độ trễ từ API đến WebSocket:{Style.RESET_ALL}")
        print(f"Tổng số client: {self.connected_clients}")
        print(f"Số client nhận được cập nhật: {sum(1 for client in self.clients if client['receive_time'] is not None)}")
        print(f"Độ trễ trung bình: {avg_latency:.2f}ms")
        print(f"Độ trễ trung vị: {median_latency:.2f}ms")
        print(f"Độ trễ tối thiểu: {min_latency:.2f}ms")
        print(f"Độ trễ tối đa: {max_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        print(f"P99: {p99_latency:.2f}ms")
        print(f"Độ lệch chuẩn: {std_dev:.2f}ms")
        
        # Phân tích thêm
        time_ranges = {
            'Dưới 10ms': 0,
            '10-50ms': 0,
            '50-100ms': 0,
            '100-200ms': 0,
            '200-500ms': 0,
            'Trên 500ms': 0
        }
        
        for t in self.propagation_times:
            if t < 10:
                time_ranges['Dưới 10ms'] += 1
            elif t < 50:
                time_ranges['10-50ms'] += 1
            elif t < 100:
                time_ranges['50-100ms'] += 1
            elif t < 200:
                time_ranges['100-200ms'] += 1
            elif t < 500:
                time_ranges['200-500ms'] += 1
            else:
                time_ranges['Trên 500ms'] += 1
                
        print(f"\n{Fore.CYAN}📈 Phân phối độ trễ:{Style.RESET_ALL}")
        for range_name, count in time_ranges.items():
            percent = (count / len(self.propagation_times)) * 100
            print(f"- {range_name}: {count} clients ({percent:.1f}%)")
    
    async def run_test(self):
        """Thực hiện đo lường và phân tích"""
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  ĐO LƯỜNG ĐỘ TRỄ TỪ API ĐẾN WEBSOCKET{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}ℹ️ Cấu hình:{Style.RESET_ALL}")
        print(f"Server URL: {self.config['server_url']}")
        print(f"API Endpoint: {self.config['api_endpoint']}")
        print(f"Số lượng clients: {self.config['client_count']}")
        
        # Tạo và kết nối các client
        await self.create_clients()
        
        # Đợi một chút để các kết nối ổn định
        await asyncio.sleep(2)
        
        # Gửi POST cập nhật
        success = await self.send_gold_update()
        
        if success:
            # Chờ tất cả client nhận được cập nhật
            await self.wait_for_all_clients_to_receive()
            
            # Phân tích và hiển thị kết quả
            self.print_summary()
            
            # Lưu kết quả
            chart_path = self.create_latency_chart()
            json_path = self.save_results_as_json()
            
            # Kết quả
            results = {
                'chart_path': chart_path,
                'json_path': json_path
            }
        else:
            results = None
            
        # Ngắt kết nối tất cả client
        await self.disconnect_clients()
        
        print(f"\n{Fore.GREEN}✓ Hoàn thành đo lường!{Style.RESET_ALL}")
        
        return results


async def main():
    parser = argparse.ArgumentParser(description='Đo lường độ trễ từ API đến WebSocket')
    
    parser.add_argument('--server', type=str, default='http://localhost:3010',
                      help='URL máy chủ (mặc định: http://localhost:3010)')
    
    parser.add_argument('--api', type=str, default='/api/add',
                      help='API endpoint để gửi cập nhật (mặc định: /api/add)')
    
    parser.add_argument('--clients', type=int, default=100,
                      help='Số lượng client WebSocket (mặc định: 100)')
    
    parser.add_argument('--verbose', action='store_true',
                      help='Hiển thị log chi tiết cho từng client')
    
    args = parser.parse_args()
    
    config = {
        'server_url': args.server,
        'api_endpoint': args.api,
        'client_count': args.clients,
        'verbose': args.verbose
    }
    
    analyzer = WSLatencyAnalyzer(config)
    results = await analyzer.run_test()
    
    # Mở biểu đồ (trong môi trường đồ họa)
    if results and results['chart_path']:
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(results['chart_path']))
        except Exception as e:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Đã hủy bởi người dùng{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Lỗi: {str(e)}{Style.RESET_ALL}") 
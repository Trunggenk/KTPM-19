#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Công cụ đo hiệu suất WebSocket cho ứng dụng Gold Price Tracker
- Khởi tạo 100 kết nối WebSocket
- Gửi POST request đến API
- Đo thời gian từ khi gửi POST đến khi tất cả client nhận được cập nhật
"""

import asyncio
import time
import json
import requests
import socketio
import argparse
import psutil
import os
import statistics
from datetime import datetime
from colorama import Fore, Style, init
from tqdm import tqdm

# Khởi tạo colorama
init(autoreset=True)

# Cấu hình mặc định
CONFIG = {
    'server_url': 'http://localhost:3010',
    'api_endpoint': '/api/add',
    'num_clients': 100,
    'test_duration': 30,  # Giây
    'update_interval': 5,  # Giây
    'result_file': 'ws_performance_results.json'
}

# Biến toàn cục
clients = []
client_receive_times = []
connected_clients = 0
disconnected_clients = 0
test_running = True
update_start_time = None
received_updates = 0
propagation_times = []
client_receive_statuses = []

class WSClient:
    """Lớp đại diện cho một kết nối WebSocket client"""
    
    def __init__(self, client_id, server_url):
        self.client_id = client_id
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False
        self.received_updates = 0
        self.last_update_time = None
        self.connect_time = None
        self.response_times = []
        self.setup_handlers()
    
    def setup_handlers(self):
        """Thiết lập các event handler cho client"""
        
        @self.sio.event
        def connect():
            global connected_clients
            self.connected = True
            self.connect_time = time.time()
            connected_clients += 1
            if CONFIG.get('verbose'):
                print(f"{Fore.GREEN}✓ Client {self.client_id} đã kết nối{Style.RESET_ALL}")
        
        @self.sio.event
        def disconnect():
            global disconnected_clients
            self.connected = False
            disconnected_clients += 1
            if CONFIG.get('verbose'):
                print(f"{Fore.RED}✗ Client {self.client_id} đã ngắt kết nối{Style.RESET_ALL}")
        
        @self.sio.on('gold-prices-updated')
        def on_gold_prices_updated(data):
            global received_updates, update_start_time, client_receive_statuses
            
            receive_time = time.time()
            self.received_updates += 1
            received_updates += 1
            
            # Nếu đây là cập nhật đầu tiên sau khi gửi POST request
            if update_start_time and client_receive_statuses[self.client_id] is None:
                propagation_time = (receive_time - update_start_time) * 1000  # chuyển đổi thành ms
                propagation_times.append(propagation_time)
                client_receive_statuses[self.client_id] = propagation_time
                
                if CONFIG.get('verbose'):
                    print(f"{Fore.CYAN}→ Client {self.client_id} nhận được cập nhật sau {propagation_time:.2f}ms{Style.RESET_ALL}")
    
    def connect(self):
        """Kết nối đến server"""
        try:
            self.sio.connect(
                self.server_url,
                transports=['websocket'],
                socketio_path='/socket.io',
                wait_timeout=10,
                headers={'clientId': str(self.client_id)}
            )
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ Lỗi khi kết nối client {self.client_id}: {str(e)}{Style.RESET_ALL}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.connected:
            try:
                self.sio.disconnect()
            except:
                pass


async def create_clients(num_clients, server_url):
    """Tạo và kết nối các client"""
    global clients, client_receive_statuses
    
    print(f"{Fore.YELLOW}⏳ Đang khởi tạo {num_clients} client...{Style.RESET_ALL}")
    progress_bar = tqdm(total=num_clients, desc="Kết nối client", unit="client")
    
    client_receive_statuses = [None] * num_clients
    
    for i in range(num_clients):
        client = WSClient(i, server_url)
        clients.append(client)
        
        # Thử kết nối
        if client.connect():
            progress_bar.update(1)
        
        # Chờ một chút giữa các kết nối để tránh quá tải
        await asyncio.sleep(0.05)
    
    progress_bar.close()
    
    # Chờ tất cả client kết nối
    timeout = 10
    start_time = time.time()
    
    print(f"{Fore.YELLOW}⏳ Đang chờ tất cả client kết nối ({timeout}s)...{Style.RESET_ALL}")
    
    while connected_clients < num_clients and time.time() - start_time < timeout:
        print(f"  Đã kết nối: {connected_clients}/{num_clients}", end="\r")
        await asyncio.sleep(0.5)
    
    if connected_clients < num_clients:
        print(f"{Fore.YELLOW}⚠ Chỉ có {connected_clients}/{num_clients} client kết nối sau thời gian chờ{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✓ Tất cả {num_clients} client đã kết nối thành công!{Style.RESET_ALL}")


def send_gold_update():
    """Gửi yêu cầu cập nhật giá vàng"""
    global update_start_time, client_receive_statuses
    
    # Reset trạng thái nhận cho mỗi client
    client_receive_statuses = [None] * len(clients)
    
    # Tạo dữ liệu cập nhật - ví dụ giá vàng
    base_price = 7500000  # Giá cơ bản
    variation = 50000     # Dao động
    
    # Tạo một đối tượng duy nhất thay vì mảng
    gold_type = 'gold_1'  # Chỉ cập nhật một loại vàng cho đơn giản
    buy_variation = int(variation * (2 * (time.time() % 1) - 1))
    sell_variation = int(variation * (2 * ((time.time() + 0.5) % 1) - 1))
    
    # Tạo đối tượng duy nhất với tất cả trường bắt buộc
    gold_data = {
        'type': gold_type,
        'name': 'VÀNG MIẾNG SJC 1L',
        'karat': '24k',
        'purity': '999.9',
        'buy_price': base_price + buy_variation,
        'sell_price': base_price + 200000 + sell_variation,
        'updated_at': datetime.now().isoformat()
    }
    
    print(f"{Fore.YELLOW}\n[{datetime.now().strftime('%H:%M:%S')}] Gửi cập nhật giá vàng...{Style.RESET_ALL}")
    # In dữ liệu sẽ gửi đi để debug
    print(f"Dữ liệu gửi đi: {json.dumps(gold_data, indent=2)}")
    
    try:
        # Ghi lại thời điểm bắt đầu cập nhật
        update_start_time = time.time()
        
        # Gửi yêu cầu POST với đối tượng duy nhất
        response = requests.post(
            f"{CONFIG['server_url']}{CONFIG['api_endpoint']}",
            json=gold_data,  # Gửi đối tượng duy nhất
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Gửi cập nhật thành công{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ Lỗi khi gửi cập nhật: HTTP {response.status_code} - {response.text}{Style.RESET_ALL}")
            update_start_time = None
            return False
            
    except Exception as e:
        print(f"{Fore.RED}✗ Lỗi khi gửi cập nhật: {str(e)}{Style.RESET_ALL}")
        update_start_time = None
        return False


def report_propagation_stats():
    """Báo cáo thống kê về thời gian lan truyền"""
    if not propagation_times:
        return
    
    # Tính các thống kê
    avg_time = sum(propagation_times) / len(propagation_times)
    min_time = min(propagation_times)
    max_time = max(propagation_times)
    
    # Tính trung vị
    median_time = statistics.median(propagation_times)
    
    # Tính độ lệch chuẩn nếu có nhiều hơn 1 mẫu
    std_dev = statistics.stdev(propagation_times) if len(propagation_times) > 1 else 0
    
    # Định nghĩa các khoảng thời gian
    time_ranges = {
        'Dưới 10ms': 0,
        '10-50ms': 0,
        '50-100ms': 0,
        '100-200ms': 0,
        '200-500ms': 0,
        'Trên 500ms': 0
    }
    
    # Phân loại thời gian
    for time_ms in propagation_times:
        if time_ms < 10:
            time_ranges['Dưới 10ms'] += 1
        elif time_ms < 50:
            time_ranges['10-50ms'] += 1
        elif time_ms < 100:
            time_ranges['50-100ms'] += 1
        elif time_ms < 200:
            time_ranges['100-200ms'] += 1
        elif time_ms < 500:
            time_ranges['200-500ms'] += 1
        else:
            time_ranges['Trên 500ms'] += 1
    
    # Hiển thị kết quả
    print(f"\n{Fore.CYAN}📊 Thống kê thời gian lan truyền:{Style.RESET_ALL}")
    print(f"  Số client nhận được cập nhật: {len(propagation_times)}/{len(clients)}")
    print(f"  Thời gian trung bình: {avg_time:.2f}ms")
    print(f"  Thời gian thấp nhất: {min_time:.2f}ms")
    print(f"  Thời gian cao nhất: {max_time:.2f}ms")
    print(f"  Thời gian trung vị: {median_time:.2f}ms")
    print(f"  Độ lệch chuẩn: {std_dev:.2f}ms")
    
    print(f"\n{Fore.CYAN}📈 Phân phối thời gian:{Style.RESET_ALL}")
    for time_range, count in time_ranges.items():
        percentage = count / len(propagation_times) * 100
        print(f"  {time_range}: {count} clients ({percentage:.1f}%)")
    
    # Lưu kết quả
    results = {
        'timestamp': datetime.now().isoformat(),
        'config': CONFIG,
        'stats': {
            'clients_total': len(clients),
            'clients_received': len(propagation_times),
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'median_time': median_time,
            'std_dev': std_dev,
            'time_distribution': {k: {'count': v, 'percentage': v / len(propagation_times) * 100} 
                                for k, v in time_ranges.items()}
        },
        'raw_data': {
            'propagation_times': propagation_times
        }
    }
    
    # Lưu vào file
    with open(CONFIG['result_file'], 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{Fore.GREEN}✓ Đã lưu kết quả vào {CONFIG['result_file']}{Style.RESET_ALL}")


async def monitor_client_receive(total_clients):
    """Theo dõi tiến trình nhận cập nhật của client"""
    global client_receive_statuses
    
    # Tạo progress bar
    pbar = tqdm(total=total_clients, desc="Clients đã nhận dữ liệu", unit="client")
    last_received = 0
    
    while test_running:
        # Đếm số client đã nhận được cập nhật
        received_count = sum(1 for status in client_receive_statuses if status is not None)
        
        # Cập nhật progress bar
        if received_count > last_received:
            pbar.update(received_count - last_received)
            last_received = received_count
        
        # Kiểm tra nếu tất cả client đã nhận được cập nhật
        if received_count == total_clients:
            pbar.close()
            print(f"{Fore.GREEN}✓ Tất cả {total_clients} client đã nhận được cập nhật!{Style.RESET_ALL}")
            report_propagation_stats()
            break
        
        await asyncio.sleep(0.1)
    
    pbar.close()


async def run_test(config):
    """Chạy bài kiểm tra hiệu suất"""
    global test_running, CONFIG, clients
    
    # Cập nhật cấu hình
    CONFIG.update(config)
    
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}⏱️  BÀI KIỂM TRA HIỆU SUẤT WEBSOCKET{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    
    # Hiển thị thông tin cấu hình
    print(f"\n{Fore.YELLOW}ℹ️ Cấu hình:{Style.RESET_ALL}")
    print(f"  Server URL: {CONFIG['server_url']}")
    print(f"  API Endpoint: {CONFIG['api_endpoint']}")
    print(f"  Số lượng client: {CONFIG['num_clients']}")
    print(f"  Thời gian chạy: {CONFIG['test_duration']}s")
    print(f"  Thời gian giữa các cập nhật: {CONFIG['update_interval']}s")
    
    # Tạo và kết nối clients
    await create_clients(CONFIG['num_clients'], CONFIG['server_url'])
    
    # Giả lập cập nhật từ API
    update_task = asyncio.create_task(send_updates())
    
    # Task theo dõi tiến trình
    monitor_task = asyncio.create_task(monitor_client_receive(CONFIG['num_clients']))
    
    # Chờ hoàn thành
    tasks = [update_task, monitor_task]
    await asyncio.gather(*tasks)
    
    # Kết thúc test
    await end_test()


async def send_updates():
    """Gửi các cập nhật theo chu kỳ"""
    global test_running
    
    # Thời điểm bắt đầu test
    start_time = time.time()
    
    # Chu kỳ gửi cập nhật
    while test_running and time.time() - start_time < CONFIG['test_duration']:
        # Gửi cập nhật
        send_gold_update()
        
        # Đợi trước lần cập nhật tiếp theo hoặc kết thúc sớm nếu hết thời gian
        remaining_time = min(
            CONFIG['update_interval'],
            CONFIG['test_duration'] - (time.time() - start_time)
        )
        
        if remaining_time <= 0:
            break
            
        # Hiển thị đếm ngược
        for i in range(int(remaining_time), 0, -1):
            if not test_running:
                break
            print(f"  Cập nhật tiếp theo sau: {i}s", end="\r")
            await asyncio.sleep(1)
    
    test_running = False


async def end_test():
    """Kết thúc bài kiểm tra và giải phóng tài nguyên"""
    global clients, test_running
    
    test_running = False
    print(f"\n{Fore.GREEN}🏁 Kết thúc bài kiểm tra{Style.RESET_ALL}")
    
    # Ngắt kết nối tất cả client
    for client in clients:
        client.disconnect()
    
    print(f"{Fore.GREEN}✓ Đã ngắt kết nối tất cả client{Style.RESET_ALL}")


def get_process_info():
    """Lấy thông tin về process hiện tại"""
    process = psutil.Process(os.getpid())
    cpu_percent = process.cpu_percent(interval=0.1)
    memory_mb = process.memory_info().rss / (1024 * 1024)
    
    return {
        'cpu_percent': cpu_percent,
        'memory_mb': memory_mb
    }


def parse_arguments():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description='Công cụ kiểm tra hiệu suất WebSocket')
    
    parser.add_argument('--server', type=str, default='http://localhost:3010',
                      help='URL máy chủ (mặc định: http://localhost:3010)')
    
    parser.add_argument('--clients', type=int, default=100,
                      help='Số lượng WebSocket client (mặc định: 100)')
    
    parser.add_argument('--duration', type=int, default=30,
                      help='Thời gian chạy bài kiểm tra, tính bằng giây (mặc định: 30)')
    
    parser.add_argument('--interval', type=int, default=5,
                      help='Khoảng thời gian giữa các cập nhật, tính bằng giây (mặc định: 5)')
    
    parser.add_argument('--verbose', action='store_true',
                      help='Hiển thị log chi tiết')
    
    parser.add_argument('--output', type=str, default='ws_performance_results.json',
                      help='File lưu kết quả (mặc định: ws_performance_results.json)')
    
    return parser.parse_args()


if __name__ == '__main__':
    # Phân tích tham số
    args = parse_arguments()
    
    # Cấu hình từ tham số
    config = {
        'server_url': args.server,
        'api_endpoint': '/api/add',
        'num_clients': args.clients,
        'test_duration': args.duration,
        'update_interval': args.interval,
        'verbose': args.verbose,
        'result_file': args.output
    }
    
    try:
        # Chạy bài kiểm tra
        asyncio.run(run_test(config))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Hủy bỏ bởi người dùng{Style.RESET_ALL}")
        asyncio.run(end_test())
    except Exception as e:
        print(f"\n{Fore.RED}✗ Lỗi: {str(e)}{Style.RESET_ALL}") 
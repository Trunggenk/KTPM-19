import asyncio
import aiohttp
import websockets
import time
import psutil
import json
from datetime import datetime
import os

async def test_nodejs_fetch(num_connections):
    start_time = time.time()
    cpu_start = psutil.cpu_percent()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_connections):
            tasks.append(session.get('http://localhost:3000/api/gold-prices'))
        responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    cpu_end = psutil.cpu_percent()
    
    return {
        'latency': (end_time - start_time) * 1000,  # Convert to ms
        'cpu_usage': cpu_end - cpu_start
    }

async def test_nodejs_websocket(num_connections):
    start_time = time.time()
    cpu_start = psutil.cpu_percent()
    
    async def connect_ws():
        async with websockets.connect('ws://localhost:3000/ws') as websocket:
            await websocket.recv()
    
    tasks = []
    for _ in range(num_connections):
        tasks.append(connect_ws())
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    cpu_end = psutil.cpu_percent()
    
    return {
        'latency': (end_time - start_time) * 1000,
        'cpu_usage': cpu_end - cpu_start
    }

async def test_golang_websocket(num_connections):
    start_time = time.time()
    cpu_start = psutil.cpu_percent()
    
    async def connect_ws():
        async with websockets.connect('ws://localhost:8080/ws') as websocket:
            await websocket.recv()
    
    tasks = []
    for _ in range(num_connections):
        tasks.append(connect_ws())
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    cpu_end = psutil.cpu_percent()
    
    return {
        'latency': (end_time - start_time) * 1000,
        'cpu_usage': cpu_end - cpu_start
    }

async def run_tests():
    connection_scales = [10, 100, 1000, 10000]
    results = {
        'nodejs_fetch': {},
        'nodejs_ws': {},
        'golang_ws': {}
    }
    
    for scale in connection_scales:
        print(f"Testing with {scale} connections...")
        
        # Test Node.js Fetch
        print("Testing Node.js Fetch...")
        results['nodejs_fetch'][str(scale)] = await test_nodejs_fetch(scale)
        
        # Test Node.js WebSocket
        print("Testing Node.js WebSocket...")
        results['nodejs_ws'][str(scale)] = await test_nodejs_websocket(scale)
        
        # Test Golang WebSocket
        print("Testing Golang WebSocket...")
        results['golang_ws'][str(scale)] = await test_golang_websocket(scale)
        
        # Wait between tests to let system stabilize
        await asyncio.sleep(5)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('test/results/comparison', exist_ok=True)
    
    with open(f'test/results/comparison/performance_data_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print("Tests completed. Results saved.")

if __name__ == "__main__":
    asyncio.run(run_tests()) 
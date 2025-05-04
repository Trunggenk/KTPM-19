@echo off

echo ===== PHAN TICH DO TRE API DEN WEBSOCKET - TEST TY LE MO RONG =====
echo.

echo Kiem tra va cai dat cac goi phu thuoc...
pip install -r requirements.txt
echo.

echo Chuan bi thu muc ket qua...
if not exist .\results mkdir .\results
if not exist .\results\scalability mkdir .\results\scalability
echo.

set SERVER_URL=http://localhost:3010
set API_ENDPOINT=/api/add

echo ===== BAT DAU PHAN TICH TY LE MO RONG =====
echo Thuc hien test voi so luong client tang dan
echo.

echo [1/3] Chay test voi 100 clients...
python ws_latency_analyzer.py --server %SERVER_URL% --api %API_ENDPOINT% --clients 100
echo.

echo [2/3] Chay test voi 1000 clients...
python ws_latency_analyzer.py --server %SERVER_URL% --api %API_ENDPOINT% --clients 1000
echo.

echo [3/3] Chay test voi 10000 clients...
python ws_latency_analyzer.py --server %SERVER_URL% --api %API_ENDPOINT% --clients 10000
echo.

echo Tong hop ket qua...
python generate_scalability_report.py
echo.

echo Da hoan thanh phan tich! Mo thu muc ket qua...
start .\results\scalability\
echo.

pause 
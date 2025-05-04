@echo off

echo ===== PHAN TICH DO TRE API DEN WEBSOCKET =====
echo.

echo Kiem tra va cai dat cac goi phu thuoc...
pip install -r requirements.txt
echo.

echo Bat dau phan tich do tre thoi gian thuc...
echo.

REM Cau hinh mac dinh
set SERVER_URL=http://localhost:3010
set API_ENDPOINT=/api/add
set CLIENT_COUNT=100

REM Cho phep tuy chinh thong qua tham so
if not "%~1"=="" set SERVER_URL=%~1
if not "%~2"=="" set API_ENDPOINT=%~2
if not "%~3"=="" set CLIENT_COUNT=%~3

echo URL Server: %SERVER_URL%
echo API Endpoint: %API_ENDPOINT%  
echo So luong clients: %CLIENT_COUNT%
echo.

python ws_latency_analyzer.py --server %SERVER_URL% --api %API_ENDPOINT% --clients %CLIENT_COUNT% 

echo.
echo Hoan thanh phan tich! Mo thu muc ket qua...
start .\results\
echo.

pause 
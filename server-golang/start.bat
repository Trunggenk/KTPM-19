@echo off
set PORT=%1
if "%PORT%"=="" set PORT=3010

echo Starting Golang server on port %PORT%...
go run cmd/server/main.go --port=%PORT% 
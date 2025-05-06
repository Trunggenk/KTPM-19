#!/bin/bash

PORT=${1:-3010}

echo "Starting Golang server on port $PORT..."
go run cmd/server/main.go --port=$PORT 
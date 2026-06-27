#!/bin/bash
echo "Building image express-gateway..."
docker build -t smartcity/express-gateway:latest ../express-gateway

echo "Building image iot-simulator..."
docker build -t smartcity/iot-simulator:latest ../iot

echo "Building image oauth-server..."
docker build -t smartcity/oauth-server:latest ../oauth-server

echo "Building image php-citizen..."
docker build -t smartcity/php-citizen:latest ../php-citizen

echo "Building image php-environment..."
docker build -t smartcity/php-environment:latest ../php-environment

echo "Building image python-ml..."
docker build -t smartcity/python-ml:latest ../python-ml

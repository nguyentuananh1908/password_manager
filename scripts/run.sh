#!/bin/bash

echo "================================"
echo "   Password Manager"
echo "================================"
echo ""

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python3 chưa được cài đặt!"
    echo "Vui lòng cài Python3 >= 3.10"
    exit 1
fi

# Kiểm tra version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}[INFO]${NC} Python version: $PYTHON_VERSION"

# Kiểm tra thư viện
echo -e "${GREEN}[INFO]${NC} Đang kiểm tra thư viện..."

if ! python3 -c "import cryptography, argon2, pyperclip, tkinter" &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} Một số thư viện chưa được cài đặt!"
    echo -e "${GREEN}[INFO]${NC} Đang tự động cài đặt..."
    echo ""
    
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Không thể cài đặt thư viện!"
        echo "Vui lòng chạy: pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo -e "${GREEN}[OK]${NC} Tất cả thư viện đã sẵn sàng!"
echo -e "${GREEN}[INFO]${NC} Đang khởi động ứng dụng..."
echo ""

# Chạy ứng dụng
python3 -m app.main

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} Ứng dụng gặp lỗi!"
    exit 1
fi


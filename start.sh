#!/bin/bash

# Function to check if Redis is installed
check_redis_installed() {
    if command -v redis-server &> /dev/null; then
        echo "Redis 已安装。"
        return 0
    else
        echo "Redis 未安装。正在安装 Redis..."
        sudo apt-get update
        sudo apt-get install -y redis-server
        sudo systemctl enable redis-server.service
        sudo systemctl start redis-server.service
        return 1
    fi
}

# Function to uninstall the Docker container and Redis
uninstall() {
    read -p "您确定要卸载 Docker 容器和 Redis 吗？[y/N] " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止并删除 Docker 容器 'redis-api'..."
        docker stop redis-api && docker rm redis-api

        echo "删除 Docker 镜像 'redis-api'..."
        docker rmi redis-api

        echo "停止并卸载 Redis..."
        sudo systemctl stop redis-server.service
        sudo apt-get purge -y redis-server
        sudo apt-get autoremove -y

        echo "已卸载 Docker 容器和 Redis。"
    else
        echo "操作取消。"
    fi
}

# Main script logic
echo "请选择操作："
echo "1. 安装 Docker 容器和 Redis"
echo "2. 卸载 Docker 容器和 Redis"
read -p "请输入选择 [1/2]: " choice

case $choice in
    1)
        # Check if Redis is installed, and install if not
        check_redis_installed

        # Clone the repository
        git clone https://github.com/ridaiqianhe/redis-api.git

        # Navigate to the cloned directory
        cd redis-api

        # Create logs directory
        mkdir -p logs

        # Build the Docker image
        docker build -t redis-api .

        # Run the Docker container
        docker run --name redis-api -v "$(pwd)":/app -e TZ=Asia/Shanghai --network host -d --restart always redis-api

        echo "Docker 容器 'redis-api' 正在运行。"
        ;;
    2)
        uninstall
        ;;
    *)
        echo "无效的选择。"
        ;;
esac

#!/bin/bash

LOG_DIR="./logs"
CRON_LOG="$LOG_DIR/cron.log"
MONITOR_SCRIPT="$(pwd)/cron_redis_api.sh"

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

# Function to create a monitoring cron job
setup_cron_job() {
    echo "设置计划任务，每5分钟检测一次服务状态..."

    # Create logs directory if not exists
    mkdir -p "$LOG_DIR"

    # Ensure the monitoring script exists
    if [[ ! -f "$MONITOR_SCRIPT" ]]; then
        echo "错误：监控脚本 $MONITOR_SCRIPT 不存在！请手动创建后重试。"
        exit 1
    fi

    # Add cron job
    CRON_JOB="*/5 * * * * $MONITOR_SCRIPT"
    (crontab -l 2>/dev/null | grep -v "$MONITOR_SCRIPT"; echo "$CRON_JOB") | crontab -

    echo "计划任务已设置。日志记录在 $CRON_LOG 中。"
}

# Function to remove cron job
remove_cron_job() {
    echo "关闭计划任务..."
    crontab -l 2>/dev/null | grep -v "$MONITOR_SCRIPT" | crontab -
    echo "计划任务已关闭。"
}

# Main script logic
echo "请选择操作："
echo "1. 安装 Docker 容器和 Redis"
echo "2. 卸载 Docker 容器和 Redis"
echo "3. 设置计划任务（每5分钟检测服务状态）"
echo "4. 关闭计划任务"
read -p "请输入选择 [1/2/3/4]: " choice

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
    3)
        setup_cron_job
        ;;
    4)
        remove_cron_job
        ;;
    *)
        echo "无效的选择。"
        ;;
esac

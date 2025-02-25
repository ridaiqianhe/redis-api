#!/bin/bash
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
CRON_LOG="/root/redis-api/logs/cron.log"

# 确保日志目录存在
mkdir -p "$(dirname "$CRON_LOG")"

if ! curl -s http://127.0.0.1:16379 > /dev/null; then
    echo "[$TIMESTAMP] 服务不可用，重启 Docker 容器..." >> "$CRON_LOG"
    docker restart redis-api >> "$CRON_LOG" 2>&1
else
    echo "[$TIMESTAMP] 服务正常。" >> "$CRON_LOG"
fi



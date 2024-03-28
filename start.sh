#!/bin/bash

docker stop redis-api && docker rm redis-api && docker rmi redis-api

git clone https://github.com/ridaiqianhe/redis-api.git

cd redis-api

mkdir logs

docker build -t redis-api .

docker run --name redis-api -v "$(pwd)":/app -e TZ=Asia/Shanghai --network host -d --restart always redis-api

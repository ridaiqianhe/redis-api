mkdir /www/wwwroot/redis-api
cd /www/wwwroot/redis-api
docker stop redis-api && docker rm redis-api && docker rmi redis-api
docker build -t redis-api .
mkdir logs
docker run --name redis-api -v /www/wwwroot/redis-api:/app -e TZ=Asia/Shanghai --network host  -d --restart always redis-api 

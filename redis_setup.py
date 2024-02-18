# redis_setup.py

import redis

# 创建全局的Redis连接池
redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)

# 创建一个Redis客户端实例并使用全局的连接池
r = redis.Redis(connection_pool=redis_pool)

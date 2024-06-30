# -*- coding:utf-8 -*-
from flask import Flask, jsonify, Response, request
import json
import time
import datetime
import os
import random
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


class Config(object):
    SESSION_KEY = os.urandom(24)
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=6)  # 设置为1小时候过期
    # SQLALCHEMY_POOL_PRE_PING = True
    JSON_AS_ASCII = False


app = Flask(__name__, template_folder='', static_folder='')
app.config.from_object(Config)


@app.route('/api/getredis/', methods=["OPTIONS", "GET", "POST"])
def getredis():
    msg = request.values.get("msg")
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f"当前时间:{timestr}\nredis获取状态{str(r.get(msg))}，剩余冻结时间{str(r.ttl(msg))}秒"


@app.route('/api/getallredis/', methods=["OPTIONS", "GET", "POST"])
def getallredis():
    keys = r.keys()
    # 获取对应的值
    values = r.mget(keys)
    # 将键和值组合成字典
    cache_data = dict(zip(keys, values))
    json_data = json.dumps(cache_data, indent=4)
    # 使用 Response 对象返回数据
    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['Charset'] = 'utf-8'
    return response


@app.route('/api/cleanup_old_data', methods=['POST', 'GET'])
def cleanup_old_data(name='yiduns', count=20000, losttime=30, rmtime=600):
    last_execution_time = r.get(f'{name}:last_execution_time')
    current_time = int(time.time())
    if not last_execution_time:
        last_execution_time = current_time-losttime
        # r.set(f'{name}:last_execution_time', current_time)
    if current_time - int(last_execution_time) <= losttime:
        return str(last_execution_time)
    else:
        r.set(f'{name}:last_execution_time', current_time)
        data = r.lrange(name, 0, -1)
        for item in data:
            splititem = item.split('###')
            if len(splititem) != 3:
                r.lrem(name, 0, item)
            else:
                token, validate, timestamp = splititem
                if current_time - int(timestamp) > rmtime:
                    r.lrem(name, 0, item)
    return '1'


@app.route('/api/readnum', methods=['POST', 'GET'])
def readnum():
    type_ = request.values['type']
    r_len = r.llen(type_)
    return {'code': 1, 'count': r_len}


@app.route('/api/yidunwrite', methods=['POST', 'GET'])
def yidunwrite():
    token = request.form['token']
    validate = request.form['validate']
    timestamp = int(time.time())
    data = f"{token}###{validate}###{timestamp}"
    r_len = r.llen('yiduns')
    if r_len >= 2000:
        cleanup_old_data('yiduns', 2000, 30, 900)
    r.rpush('yiduns', data)
    return {'code': 1, 'count': r_len}


@app.route('/api/yidunread', methods=['GET'])
def yidunread():
    type_ = request.values.get('type')
    r_len = r.llen('yiduns')
    if r_len <= 30 and str(type_) != '1':
        return {"count": 0, 'msg': r_len}
    data = r.lrange('yiduns', 0, -1)
    if not data:
        return {"count": 0}
    else:
        value = random.choice(data[-100:])
        value1 = value.split('###')
        token, validate = value1[0], value1[1]
        try:
            t = value1[2]
        except:
            t = 1
        r.lrem('yiduns', 1, value)
        result = {"token": token, "validate": validate,
                  "count": len(data)-1, 't': t}
        return result


@app.route('/api/slidewrite', methods=['POST', 'GET'])
def slidewrite():
    token = request.form['token']
    validate = request.form['validate']
    timestamp = int(time.time())
    data = f"{token}###{validate}###{timestamp}"
    r_len = r.llen('slides')
    # Check and trim the list if it exceeds 20000 items
    if r_len >= 200:
        cleanup_old_data('slides', 200, 60, 900)
    r.rpush('slides', data)
    return {'code': 1, 'count': r_len}


@app.route('/api/slideread', methods=['GET'])
def slideread():
    # cleanup_old_data('slides',2000)

    type_ = request.values.get('type')
    r_len = r.llen('slides')
    if r_len <= 30 and str(type_) != '1':
        return {"count": 0, 'msg': r_len}
    data = r.lrange('slides', 0, -1)
    if not data:
        return {"count": 0}
    else:
        value = random.choice(data[-100:])
        value1 = value.split('###')
        token, validate = value1[0], value1[1]
        r.lrem('slides', 1, value)
        try:
            t = value1[2]
        except:
            t = 1
        result = {"token": token, "validate": validate,
                  "count": len(data)-1, 't': t}
        return result


@app.errorhandler(404)
def error_date(error):
    return '''＿ ˍ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▏ ▎ ▍ ▌ ▋ ▊ ▉ ◪ ◫ ☖ ☗ ▓ ░ ▒ ❑ ❒ ❖ ❚ ⊞ ⊟ ⊠ ⊡ ⎔ ▀ ▯ ▮ ▰ ▱ ◩ ⧄ ⧅ ⧆ ⧇ ⧈ ⧯⧮<br>Welcome to redis-api
'''


if __name__ == '__main__':
    app.run(port=10000, host="0.0.0.0", debug=True)

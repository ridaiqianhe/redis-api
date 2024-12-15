# -*- coding:utf-8 -*-
from flask import Flask, jsonify, request
import time
import os
import random
import redis

# Redis 连接设置
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


class Config(object):
    JSON_AS_ASCII = False


app = Flask(__name__)
app.config.from_object(Config)


def cleanup_old_data(name='slides', rmtime=900):
    """清理过期的数据"""
    current_time = int(time.time())
    # 删除分数（时间戳）在当前时间之前超过 rmtime 的数据
    r.zremrangebyscore(name, '-inf', current_time - rmtime)
    return '1'


@app.route('/api/slideread', methods=['GET'])
def slideread():
    """读取 slide 数据"""
    cleanup_old_data('slides', rmtime=900)
    type_ = request.values.get('type')
    r_len = r.zcard('slides')
    if r_len <= 30 and str(type_) != '1':
        return jsonify({"count": 0, 'msg': r_len})
    # 获取所有数据
    data = r.zrange('slides', 0, -1)
    if not data:
        return jsonify({"count": 0})
    else:
        value = random.choice(data[-100:])
        token, validate = value.split('###')
        # 删除已读取的数据
        r.zrem('slides', value)
        result = {"token": token, "validate": validate,
                  "count": r_len - 1}
        return jsonify(result)


@app.route('/api/slidewrite', methods=['POST'])
def slidewrite():
    """写入 slide 数据"""
    token = request.form.get('token')
    validate = request.form.get('validate')
    if not token or not validate:
        return jsonify({'code': 0, 'msg': '参数缺失'})
    timestamp = int(time.time())
    data = f"{token}###{validate}"
    r.zadd('slides', {data: timestamp})
    # 限制集合的最大长度
    r.zremrangebyrank('slides', 0, -3001)
    return jsonify({'code': 1, 'count': r.zcard('slides')})


@app.route('/api/yidunread', methods=['GET'])
def yidunread():
    """读取 yidun 数据"""
    cleanup_old_data('yiduns', rmtime=900)
    type_ = request.values.get('type')
    r_len = r.zcard('yiduns')
    if r_len <= 30 and str(type_) != '1':
        return jsonify({"count": 0, 'msg': r_len})
    # 获取所有数据
    data = r.zrange('yiduns', 0, -1)
    if not data:
        return jsonify({"count": 0})
    else:
        value = random.choice(data[-100:])
        token, validate = value.split('###')
        # 删除已读取的数据
        r.zrem('yiduns', value)
        result = {"token": token, "validate": validate,
                  "count": r_len - 1}
        return jsonify(result)


@app.route('/api/yidunwrite', methods=['POST'])
def yidunwrite():
    """写入 yidun 数据"""
    token = request.form.get('token')
    validate = request.form.get('validate')
    if not token or not validate:
        return jsonify({'code': 0, 'msg': '参数缺失'})
    timestamp = int(time.time())
    data = f"{token}###{validate}"
    r.zadd('yiduns', {data: timestamp})
    # 限制集合的最大长度
    r.zremrangebyrank('yiduns', 0, -3001)
    return jsonify({'code': 1, 'count': r.zcard('yiduns')})


@app.route('/api/readnum', methods=['GET'])
def readnum():
    """读取指定类型的数据数量"""
    type_ = request.values.get('type')
    if not type_:
        return jsonify({'code': 0, 'msg': '参数缺失'})
    if type_ not in ['slides', 'yiduns']:
        return jsonify({'code': 0, 'msg': '类型错误'})
    r_len = r.zcard(type_)
    return jsonify({'code': 1, 'count': r_len})


@app.errorhandler(404)
def error_date(error):
    """处理 404 错误"""
    return '''Welcome to redis-api
    ''', 404


if __name__ == '__main__':
    app.run(port=10000, host="0.0.0.0", debug=False)

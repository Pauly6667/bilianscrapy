import redis

redis_conn = redis.StrictRedis(
    host = 'localhost',
    port = 6379,
    password = '',
    decode_responses = True,
)

ret = redis_conn.execute_command('')
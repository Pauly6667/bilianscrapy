import redis
import time
from random import choice
proxlpool = [
    '39.137.95.74:80',
    '39.137.95.69:8080',
    '39.137.69.10:80',
    '39.137.69.8:8080',
    '221.180.170.104:8080',
    '101.4.136.34:81',
    '39.137.69.7:8080',
    '123.169.99.84:9999',
    '60.182.27.198:8118',
    '182.46.206.19:9999',
    '113.124.159.154:8118',
    '117.60.19.91:8118',
    '180.127.218.232:9999',
    '163.204.247.147:9999'
]
class ProxyPool():
    def __init__(self):
        self.redis_conn = redis.StrictRedis(
            host='localhost',
            port=6379,
            decode_responses=True,
        )

    def set_proxy(self):
        proxy_odd = None
        while True:
            proxy_new = choice(proxlpool)
            if proxy_new != proxy_odd:
                proxy_odd = proxy_new
                self.redis_conn.delete('proxy')
                self.redis_conn.sadd('proxy',proxy_new)
                print('更更换的代理ip',proxy_new)
                time.sleep(3)
            else:
                time.sleep(3)
    def get_proxy(self):
        proxy_s = self.redis_conn.srandmember('proxy',1)
        if proxy_s:
            return proxy_s[0]
            # print(proxy_s)
        else:
            time.sleep(0.1)
            return self.get_proxy()
if __name__ == '__main__':
    # ProxyPool().set_proxy()
    ProxyPool().get_proxy()
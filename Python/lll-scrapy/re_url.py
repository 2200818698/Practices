import redis

conn = redis.Redis(host='127.0.0.1',port=6379)

# 考点a
# 起始url的Key： chouti:start_urls
conn.lpush("chouti:start_urls",'https://dig.chouti.com')
# 起始url的Key： down:start_urls
conn.lpush("down:start_urls",'https://dig.chouti.com')
# 清空
# conn.flushdb()
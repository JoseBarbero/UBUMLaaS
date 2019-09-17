from ubumlaas import celery
from celery.task.base import periodic_task
from config import config, Config
 
# Set Redis connection:
redis_url = urlparse.urlparse(Config.REDIS_URL)
r = redis.StrictRedis(host=redis_url.hostname, port=redis_url.port, db=1, password=redis_url.password)
 
# Test the Redis connection:
try: 
    r.ping()
    print "Redis is connected!"
except redis.ConnectionError:
    print "Redis connection error!"
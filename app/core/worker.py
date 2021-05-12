import redis
from rq import Worker, Queue, Connection
import app.core.config as config

listen = ['default']

redis_url = config.REDIS_URL

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work(with_scheduler=True)
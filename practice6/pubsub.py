import concurrent.futures
import logging
import pika
import random
import json
import time
from pika.exchange_type import ExchangeType

# константы подключения
RABBIT_HOST = "xexeapp.site"
RABBIT_QUEUE_NAME = "sample-test-queue"
RABBIT_EXCHANGE_NAME = "sample-test-exchange2"
RABBIT_USER = "rabbitmq"
RABBIT_PASSWORD = "6ad6wd7w7dw76dw6d7w8976d8wdw75d7w5d0"

# конфигурация
params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD))
logging.basicConfig(level=logging.WARN)

# код продюсера в бесконечном цикле
def producer():
    time.sleep(1)
    rnd = random.Random()
    connection = pika.BlockingConnection(params)
    local = connection.channel()
    local.exchange_declare(RABBIT_EXCHANGE_NAME, ExchangeType.fanout)
    id = 0

    while True:
        # формируем примитивный объект в JSON
        obj = {
            "id": id,
            "user": rnd.choice(["morpheus", "neo", "trinity"]),
            "code": rnd.randint(0, 9999),
            "hex": '%030x' % rnd.randrange(16**30)
        }
        local.basic_publish(exchange=RABBIT_EXCHANGE_NAME, routing_key='', body=json.dumps(obj).encode("utf-8"))
        logging.warning(f"[PROD] Produced: {obj}")
        id += 1
        time.sleep(0.5)

# код консюмера
def consumer(cons_id):
    def callback(ch, method, properties, body):
        logging.warning(f"[{cons_id}] Consumed: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = pika.BlockingConnection(params)
    local = connection.channel()
    local.exchange_declare(RABBIT_EXCHANGE_NAME, ExchangeType.fanout)

    queue = local.queue_declare("", exclusive=True, auto_delete=True)
    local.queue_bind(exchange=RABBIT_EXCHANGE_NAME, queue=queue.method.queue)
    local.basic_consume(queue.method.queue, on_message_callback=callback)

    local.start_consuming()

# создадим и запустим одного продюсера и двух консюмеров
pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
futures = [pool.submit(producer), pool.submit(consumer, 0), pool.submit(consumer, 1)]

concurrent.futures.wait(futures)

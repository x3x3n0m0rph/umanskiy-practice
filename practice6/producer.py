import concurrent.futures
import logging
import pika
import random
import json

QUEUE_NAME = "sample-test-queue"
params = pika.ConnectionParameters(host="xexeapp.site", credentials=pika.PlainCredentials('rabbitmq', '6ad6wd7w7dw76dw6d7w8976d8wdw75d7w5d0'))
logging.basicConfig(level=logging.INFO)


def producer():
    rnd = random.Random()
    connection = pika.BlockingConnection(params)
    local = connection.channel()
    local.queue_declare(queue=QUEUE_NAME)
    id = 0

    while True:
        obj = {
            "id": id,
            "user": rnd.choice(["leo", "neo", "trinity"]),
            "code": rnd.randint(0, 9999),
            "hex": '%030x' % rnd.randrange(16**30)
        }
        local.basic_publish('', QUEUE_NAME, json.dumps(obj).encode("utf-8"))
        id += 1


def consumer(cons_id):
    def callback(ch, method, properties, body):
        logging.info(f"[{cons_id}] Received: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = pika.BlockingConnection(params)
    local = connection.channel()
    local.queue_declare(queue=QUEUE_NAME)
    local.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    local.start_consuming()


pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
futures = [pool.submit(producer), pool.submit(consumer, 0), pool.submit(consumer, 1)]
concurrent.futures.wait(futures)

import json
from typing import Any

from confluent_kafka import Producer

producer_conf = {
    'bootstrap.servers': 'localhost:29092'
}

producer = Producer(producer_conf)


def send_task(key, value, topic = 'visa-es-orders', callback=lambda err, msg: delivery_report(err, msg)):
    if isinstance(value, dict):
        value = json.dumps(value)

    producer.produce(topic, key=key, value=value.encode('utf-8'), callback=callback)
    producer.flush()
    print(f'Task {key} added to queue')

def retry_task(key, value, topic = 'visa-es-orders', callback=lambda err, msg: delivery_report(err, msg)):
    if isinstance(value, dict):
        value = json.dumps(value)

    producer.produce(topic, key=key, value=value.encode('utf-8'), callback=callback)
    producer.flush()
    print(f"❌ Task {key} failed, re-enqueued for retrying")

def delivery_report(err: Any, msg: Any):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

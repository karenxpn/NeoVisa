import json

from confluent_kafka import Producer

producer_conf = {
    'bootstrap.servers': 'localhost:29092'
}

producer = Producer(producer_conf)


async def send_task(key, value, topic = 'visa-es-orders'):

    if isinstance(value, dict):
        value = json.dumps(value)

    from order.models import OrderStatus
    from order.services import OrderService

    await OrderService.update_order_status(int(key), OrderStatus.PROCESSING)

    producer.produce(topic, key=key, value=value.encode('utf-8'))
    producer.flush()
    print(f'Task {key} added to queue')

async def retry_task(key, value, topic = 'visa-es-orders'):
    if isinstance(value, dict):
        value = json.dumps(value)

    producer.produce(topic, key=key, value=value.encode('utf-8'))
    producer.flush()
    print(f"❌ Task {key} failed, re-enqueued for retrying")

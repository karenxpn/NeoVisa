import json
import time

from confluent_kafka import Consumer, KafkaException
from core.kafka_producer import retry_task, send_task

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'task-processor-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['visa-orders'])


def process_task(order_data):
    print(f"Processing Order {order_data['order_id']}...")
    success = int(order_data['order_id']) % 2 == 0  # Simulate success/failure
    return success


while True:
    print("Polling for messages...")

    try:
        msg = consumer.poll(5.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        order_data = json.loads(msg.value().decode('utf-8'))
        order_id = order_data['order_id']

        time.sleep(5)

        if process_task(order_data):
            print(f"✅ Task {order_id} succeeded, removed from queue")
        else:
            retry_task(str(order_id), json.dumps(order_data))
        consumer.commit()

    except KafkaException as e:
        print(f'Kafka error: {e}')
    except Exception as e:
        print(f"Error while consuming: {e}")


consumer.close()

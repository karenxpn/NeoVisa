from confluent_kafka import Consumer, KafkaException

from core.kafka_producer import retry_task, send_task

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'task-processor-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['task-queue'])

def process_task(task_id):
    print(f"Processing {task_id}...")
    success = int(task_id) % 2 == 0
    return success


for i in range(10):
    send_task(i)


while True:
    print("Polling for messages...")

    try:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        task_id = msg.value().decode('utf-8')
        if process_task(task_id):
            consumer.commit()
            print(f"✅ Task {task_id} succeeded, removed from queue")
        else:
            retry_task(task_id)
    except KafkaException as e:
        print(f'Kafka error: {e}')
    except Exception as e:
        print(f"Error while consuming: {e}")


consumer.close()

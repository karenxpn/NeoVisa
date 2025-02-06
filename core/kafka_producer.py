from confluent_kafka import Producer

producer_conf = {
    'bootstrap.servers': 'localhost:29092'
}

producer = Producer(producer_conf)


def send_task(task_id):
    producer.produce('task-queue', key=str(task_id), value=str(task_id))
    producer.flush()
    print(f'Task {task_id} added to queue')

def retry_task(task_id):
    producer.produce('task-queue', key=str(task_id), value=str(task_id))
    producer.flush()
    print(f"❌ Task {task_id} failed, re-enqueued for retrying")

from confluent_kafka import Producer

producer_conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(producer_conf)


def send_task(task_id):
    producer.produce('task-queue', key=str(task_id), value=f'Task {task_id}')
    producer.flush()
    print(f'Task {task_id} added to queue')


for i in range(10):
    send_task(i)

import asyncio
import json
import time

from confluent_kafka import Consumer, KafkaException
from core.kafka_producer import retry_task, send_task
from order.order_serializer import OrderSerializer
from visa_center.models import CountryEnum
from visa_center.services import VisaCenterService

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'task-processor-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['visa-orders'])


async def process_task(order):
    print('Processing order: {}'.format(order))

    visa_center = order.visa_credentials
    if visa_center.country == CountryEnum.ES:
        print('Valid visa center')
    else:
        print('Invalid Visa Center')
    # order = OrderSerializer.model_validate(order_data, partial=True)
    # print(f"Processing Order {order}...")
    #
    # visa_center = order_data['visa_credentials']['visa_country']
    # print(f"Visa Center: {visa_center}")
    #
    # if visa_center == CountryEnum.ES:
    #     username = order_data['visa_credentials']['username']
    #     password = order_data['visa_credentials']['password']
    #
    #     await VisaCenterService().run_visa_authentication(username, password)
    # else:
    #     print('Invalid Visa Center')
    #
    # success = int(order_data['order_id']) % 2 == 0  # Simulate success/failure
    return True


async def consume_tasks():
    while True:
        print("Polling for messages...")

        try:
            msg = consumer.poll(5.0)

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue


            order = OrderSerializer.model_validate(
                json.loads(msg.value().decode('utf-8'))
            )
            order_id = order.id

            await asyncio.sleep(5)

            result = await process_task(order)
            if result:
                print(f"✅ Task {order_id} succeeded, removed from queue")
            else:
                retry_task(str(order_id), json.dumps(order))
            consumer.commit()

        except KafkaException as e:
            print(f'Kafka error: {e}')
        except Exception as e:
            print(f"Error while consuming: {e}")


    consumer.close()


if __name__ == '__main__':
    asyncio.run(consume_tasks())

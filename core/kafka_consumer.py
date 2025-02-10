import asyncio
import json
import time

from confluent_kafka import Consumer, KafkaException
from sqlalchemy import select

from core.database import get_db
from core.kafka_producer import retry_task, send_task
from core.proceed_request import proceed_request
from order.order_serializer import OrderSerializer
from visa_center.models import CountryEnum, VisaCenterCredentials
from visa_center.services import VisaCenterService

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'task-processor-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['visa-es-orders'])

async def get_visa_credentials(id: int):
    async for db in get_db():
        result = await db.execute(
            select(VisaCenterCredentials)
            .where(VisaCenterCredentials.id == id)
        )
        return result.scalar_one_or_none()



async def process_task(order):
    print('Processing order: {}'.format(order))

    visa_center = await get_visa_credentials(order.visa_credentials.id)

    if visa_center.country == CountryEnum.ES:
        try:
            await VisaCenterService().run_visa_authentication(visa_center)
        except KafkaException as e:
            print(e)
        except Exception as e:
            print(e)
    else:
        print('Invalid Visa Center')

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

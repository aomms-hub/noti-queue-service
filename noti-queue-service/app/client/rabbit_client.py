import aio_pika
import json
from typing import Optional
from config import RABBITMQ_URL, EXCHANGE_NAME, ROUTING_KEY

class RabbitClient:
    def __init__(self, url: str = RABBITMQ_URL):
        self.url = url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

    async def connect(self):
        if self.connection and not self.connection.is_closed:
            return
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def publish_message(self, amount: str, title: str, time: str):
        payload = {
            "amount": amount,
            "time": time,
            "source": title
        }

        if not self.exchange:
            raise Exception("Exchange not initialized. Call connect() first.")

        msg = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await self.exchange.publish(msg, routing_key=ROUTING_KEY)

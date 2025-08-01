import asyncio
import time
import aio_pika
import json
from datetime import datetime
from config import RABBITMQ_URL, EXCHANGE_NAME, ROUTING_KEY


class RabbitClient:
    def __init__(self, url: str = RABBITMQ_URL, idle_timeout=300):
        self.url = url
        self.connection = None
        self.channel = None
        self.exchange = None
        self.last_activity = time.time()
        self.idle_timeout = idle_timeout  # วินาที
        self.idle_task = None

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
        if not self.idle_task:
            self.idle_task = asyncio.create_task(self._idle_watcher())

    async def _idle_watcher(self):
        while True:
            await asyncio.sleep(10)
            idle_time = time.time() - self.last_activity
            if idle_time > self.idle_timeout:
                print(f"Idle timeout {self.idle_timeout}s reached. Closing connection...")
                await self.close()
                self.idle_task = None
                break

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None
        if self.idle_task:
            self.idle_task.cancel()
            self.idle_task = None

    async def publish_message(self, amount: str, title: str, timestamp: datetime):
        if not self.connection or self.connection.is_closed:
            await self.connect()

        self.last_activity = time.time()

        payload = {
            "amount": amount,
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "source": title
        }

        msg = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await self.exchange.publish(msg, routing_key=ROUTING_KEY)

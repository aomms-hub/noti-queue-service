from app.services.redis_service import is_consumer_active
from app.client.pay_alert_composite_client import start_consumer
from app.client.rabbit_client import RabbitClient
from datetime import datetime

rabbit_client = RabbitClient()


async def publish_amount_message(amount: str, source: str, timestamp: datetime):
    if not is_consumer_active():
        await start_consumer()
    await rabbit_client.publish_message(amount, source, timestamp)

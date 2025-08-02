from fastapi import FastAPI
from pydantic import BaseModel
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from contextlib import asynccontextmanager
from app.client.rabbit_client import RabbitClient
from app.services.notification_service import publish_amount_message
from config import TIME_ZONE

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")

rabbit_client = RabbitClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.info("Starting lifespan: connecting to RabbitMQ...")
        await rabbit_client.connect()
        logging.info("Connected to RabbitMQ!")
        yield
    except Exception as e:
        logging.error(f"Error in lifespan startup: {e}")
        raise e
    finally:
        logging.info("Closing RabbitMQ connection...")
        await rabbit_client.close()
        logging.info("RabbitMQ connection closed.")


app = FastAPI(lifespan=lifespan)


class NotificationRequest(BaseModel):
    message: str
    title: str
    timestamp: str


def extract_exact_amount(message: str) -> str:
    match = re.search(r"\b\d{1,12}\.\d{2}\b", message)
    if match:
        return match.group(0)
    return "invalid amount message"


@app.post("/notify")
async def receive_notification(notification: NotificationRequest):
    timestamp = datetime.now(ZoneInfo(TIME_ZONE))
    amount = extract_exact_amount(notification.message)
    if amount == "invalid amount message":
        return {"status": "error", "detail": "Invalid amount format."}
    await publish_amount_message(amount=amount, source=notification.title, timestamp=timestamp)
    return {
        "status": "received",
        "amount": amount,
        "timestamp": timestamp
    }

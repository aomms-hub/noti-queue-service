from fastapi import FastAPI
from pydantic import BaseModel
import re
import datetime
import logging
from contextlib import asynccontextmanager
from app.client.rabbit_client import RabbitClient

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
    match = re.search(r"\b\d{1,3}\.\d{2}\b", message)
    if match:
        return match.group(0)
    return "invalid amount message"


@app.post("/notify")
async def receive_notification(notification: NotificationRequest):
    amount = extract_exact_amount(notification.message)
    await rabbit_client.publish_message(amount, notification.title, notification.timestamp)
    return {
        "status": "received",
        "amount": amount,
        "timestamp": datetime.datetime.now()
    }

import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

EXCHANGE_NAME = "notification.queue.amount"
ROUTING_KEY = "notify.amount.parsed"
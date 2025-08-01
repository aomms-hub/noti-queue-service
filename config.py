import os
from dotenv import load_dotenv

load_dotenv()

TIME_ZONE = "Asia/Bangkok"

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")

EXCHANGE_NAME = "notification.queue.amount"
ROUTING_KEY = "notify.amount.parsed"

PAY_ALERT_COMPOSITE_URL = "https://pay-alert-composite-production.up.railway.app"
START_CONSUMER_PATH = "/consumer/start"
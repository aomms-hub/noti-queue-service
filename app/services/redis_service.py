from app.client.redis_client import redis_client

CONSUMER_STATUS_REDIS_KEY = "consumer:status:"
PAY_ALERT_COMPOSITE_SERVICE_NAME = "pay-alert-composite"
CONSUMER_ACTIVE_STATUS = "active"

def is_consumer_active()-> bool:
    key = f"{CONSUMER_STATUS_REDIS_KEY}{PAY_ALERT_COMPOSITE_SERVICE_NAME}"
    value = redis_client.get(key)
    if value == CONSUMER_ACTIVE_STATUS:
        return True
    return False

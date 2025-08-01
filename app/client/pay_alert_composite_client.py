import httpx
import logging
from config import PAY_ALERT_COMPOSITE_URL, START_CONSUMER_PATH
from pydantic import BaseModel

class TTSResponse(BaseModel):
    from_cache: bool
    audio_url: str

async def start_consumer():
    url = f"{PAY_ALERT_COMPOSITE_URL}{START_CONSUMER_PATH}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            response.raise_for_status()
        logging.info(f"✅ Sent request to start consumer with response: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Failed toSent request to start consumer with response: {e}")
        raise

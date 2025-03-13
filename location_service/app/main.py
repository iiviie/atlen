from fastapi import FastAPI, HTTPException, Depends, Header
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
from .config import settings
import time
import logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Location Service")

def get_kafka_producer():
    retries = 5
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            return producer
        except NoBrokersAvailable:
            retries -= 1
            if retries == 0:
                logger.error("Failed to connect to Kafka after 5 attempts")
                raise
            logger.warning(f"Kafka not available, retrying... {retries} attempts left")
            time.sleep(5)

producer = get_kafka_producer()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.post("/locations/", dependencies=[Depends(verify_api_key)])
async def update_location(data: dict):
    try:
        producer.send(settings.KAFKA_TOPIC, value=data)
        return {"message": "Location update sent successfully"}
    except Exception as e:
        logger.error(f"Error sending location update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

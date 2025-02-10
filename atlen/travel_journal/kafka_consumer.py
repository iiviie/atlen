from kafka import KafkaConsumer
from django.conf import settings
import json
import logging
import time
from .models import LocationUpdate
from trip.models import Trip
from django.contrib.auth import get_user_model
import threading
from kafka.errors import NoBrokersAvailable

logger = logging.getLogger(__name__)

class TravelJournalConsumer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.consumer = None
        self.should_run = True
        self.daemon = True

    def connect_kafka(self):
        retries = 5
        while retries > 0 and self.should_run:
            try:
                logger.info("Attempting to connect to Kafka...")
                self.consumer = KafkaConsumer(
                    settings.KAFKA_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    group_id='travel_journal_group',
                    auto_offset_reset='latest'
                )
                logger.info("Successfully connected to Kafka")
                return True
            except NoBrokersAvailable:
                retries -= 1
                logger.warning(f"Failed to connect to Kafka. Retries left: {retries}")
                time.sleep(5)
        return False

    def run(self):
        if not self.connect_kafka():
            logger.error("Failed to connect to Kafka after all retries")
            return

        try:
            for message in self.consumer:
                if not self.should_run:
                    break
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {str(e)}")
        finally:
            if self.consumer:
                self.consumer.close()

    def stop(self):
        self.should_run = False
        if self.consumer:
            self.consumer.close()

    def process_message(self, data):
        try:
            logger.info(f"Received location update: {data}")
            User = get_user_model()
            trip = Trip.objects.get(id=data['trip_id'])
            user = User.objects.get(id=data['user_id'])
            
            location = LocationUpdate.objects.create(
                trip=trip,
                user=user,
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            logger.info(f"Created location update: {location.id}")
        except Trip.DoesNotExist:
            logger.error(f"Trip not found with ID: {data.get('trip_id')}")
        except User.DoesNotExist:
            logger.error(f"User not found with ID: {data.get('user_id')}")
        except Exception as e:
            logger.error(f"Error processing location update: {str(e)}") 
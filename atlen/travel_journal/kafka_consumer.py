from kafka import KafkaConsumer
from django.conf import settings
import json
import logging
from .models import LocationUpdate
from trip.models import Trip
from django.contrib.auth import get_user_model
import threading

logger = logging.getLogger(__name__)

class TravelJournalConsumer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='travel_journal_group',
            auto_offset_reset='latest'
        )
        self.daemon = True

    def run(self):
        try:
            for message in self.consumer:
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {str(e)}")
            self.consumer.close()

    def process_message(self, data):
        try:
            User = get_user_model()
            trip = Trip.objects.get(id=data['trip_id'])
            user = User.objects.get(id=data['user_id'])
            
            LocationUpdate.objects.create(
                trip=trip,
                user=user,
                latitude=data['latitude'],
                longitude=data['longitude']
            )
        except Exception as e:
            logger.error(f"Error processing location update: {str(e)}") 
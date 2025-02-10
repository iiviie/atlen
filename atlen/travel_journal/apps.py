from django.apps import AppConfig
import sys
import logging

logger = logging.getLogger(__name__)


class TravelJournalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'travel_journal'

    def ready(self):
        if 'runserver' in sys.argv:
            try:
                from .kafka_consumer import TravelJournalConsumer
                consumer = TravelJournalConsumer()
                consumer.start()
                logger.info("Kafka consumer started successfully")
            except Exception as e:
                logger.error(f"Failed to start Kafka consumer: {str(e)}")

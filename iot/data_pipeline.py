"""Data pipeline orchestrator for IoT data ingestion.

Coordinates MQTT, AWS IoT Core, SQS, and OPC-UA data sources
into a unified processing pipeline.
"""

import json
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.reading import SensorReading
from app.models.sensor import Sensor

logger = get_logger(__name__)


class DataPipeline:
    """
    Unified data pipeline that processes sensor data from all sources.

    Flow:
        IoT Sources → Validation → Enrichment → Storage → AI Trigger
    """

    def __init__(self):
        self.mqtt_subscriber = None
        self.aws_iot_client = None
        self.sqs_consumer = None
        self._message_count = 0
        self._error_count = 0

    def process_message(self, message: dict):
        """
        Process a sensor message from any source.

        Args:
            message: Sensor data dict with sensor_id, value, timestamp, etc.
        """
        try:
            self._message_count += 1

            # Validate message
            if not self._validate_message(message):
                self._error_count += 1
                return

            # Store reading in database
            self._store_reading(message)

            logger.debug(
                "Message processed",
                sensor_id=message.get("sensor_id"),
                source=message.get("source", "unknown"),
            )

        except Exception as e:
            self._error_count += 1
            logger.error("Pipeline processing error", error=str(e))

    def _validate_message(self, message: dict) -> bool:
        """Validate incoming sensor message."""
        required_fields = ["sensor_id", "value"]
        for field in required_fields:
            if field not in message or message[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate value is numeric
        try:
            float(message["value"])
        except (TypeError, ValueError):
            logger.warning("Invalid numeric value", value=message.get("value"))
            return False

        return True

    def _store_reading(self, message: dict):
        """Store a validated reading in the database."""
        db = SessionLocal()
        try:
            # Look up sensor by string ID
            sensor = (
                db.query(Sensor)
                .filter(Sensor.sensor_id == message["sensor_id"])
                .first()
            )

            if not sensor:
                logger.warning(
                    "Unknown sensor ID, skipping",
                    sensor_id=message["sensor_id"],
                )
                return

            # Parse timestamp
            timestamp = message.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                )
            elif not timestamp:
                timestamp = datetime.utcnow()

            reading = SensorReading(
                sensor_id=sensor.id,
                value=float(message["value"]),
                timestamp=timestamp,
                quality=message.get("quality", 100),
                source=message.get("source", "unknown"),
            )
            db.add(reading)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error("Database storage error", error=str(e))
        finally:
            db.close()

    def start(self):
        """Start all configured IoT data sources."""
        logger.info("Starting data pipeline...")

        # Start MQTT subscriber
        try:
            from iot.mqtt_subscriber import MQTTSubscriber

            self.mqtt_subscriber = MQTTSubscriber(
                on_message_callback=self.process_message
            )
            self.mqtt_subscriber.start()
        except Exception as e:
            logger.warning(f"MQTT subscriber not started: {e}")

        # Start SQS consumer
        try:
            from iot.sqs_consumer import SQSConsumer

            self.sqs_consumer = SQSConsumer(
                on_message_callback=self.process_message
            )
            self.sqs_consumer.start()
        except Exception as e:
            logger.warning(f"SQS consumer not started: {e}")

        logger.info("Data pipeline started")

    def stop(self):
        """Stop all IoT data sources."""
        if self.mqtt_subscriber:
            self.mqtt_subscriber.stop()
        if self.sqs_consumer:
            self.sqs_consumer.stop()
        logger.info("Data pipeline stopped")

    def get_stats(self) -> dict:
        """Get pipeline statistics."""
        return {
            "messages_processed": self._message_count,
            "errors": self._error_count,
            "mqtt_connected": (
                self.mqtt_subscriber.is_connected if self.mqtt_subscriber else False
            ),
            "sqs_running": (
                self.sqs_consumer.is_running if self.sqs_consumer else False
            ),
        }

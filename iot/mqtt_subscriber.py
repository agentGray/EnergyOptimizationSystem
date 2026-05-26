"""MQTT subscriber for real-time sensor data ingestion.

Subscribes to factory sensor topics and forwards data to the processing pipeline.
Supports both local MQTT brokers and AWS IoT Core.
"""

import json
import time
import threading
from datetime import datetime
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MQTTSubscriber:
    """
    MQTT subscriber that listens to factory sensor topics.

    Topic structure:
        {prefix}/{zone}/{asset_tag}/{sensor_id}
        Example: factory/sensors/zone-a/chiller-01/temperature

    Message format (JSON):
        {
            "sensor_id": "TEMP-001",
            "value": 72.5,
            "timestamp": "2024-01-15T10:30:00Z",
            "quality": 100,
            "unit": "°C"
        }
    """

    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.client = mqtt.Client(
            client_id=f"energy-optimizer-{int(time.time())}",
            protocol=mqtt.MQTTv311,
        )
        self.broker_host = settings.MQTT_BROKER_HOST
        self.broker_port = settings.MQTT_BROKER_PORT
        self.topic_prefix = settings.MQTT_TOPIC_PREFIX
        self.on_message_callback = on_message_callback
        self._is_connected = False
        self._reconnect_delay = 5

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Authentication
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self._is_connected = True
            logger.info(
                "Connected to MQTT broker",
                host=self.broker_host,
                port=self.broker_port,
            )
            # Subscribe to all sensor topics
            topic = f"{self.topic_prefix}/#"
            client.subscribe(topic, qos=1)
            logger.info("Subscribed to topic", topic=topic)
        else:
            logger.error("MQTT connection failed", return_code=rc)

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self._is_connected = False
        if rc != 0:
            logger.warning(
                "Unexpected MQTT disconnection, will reconnect",
                return_code=rc,
            )

    def _on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))

            # Parse topic to extract metadata
            topic_parts = topic.replace(self.topic_prefix + "/", "").split("/")

            sensor_data = {
                "topic": topic,
                "sensor_id": payload.get("sensor_id"),
                "value": payload.get("value"),
                "timestamp": payload.get("timestamp", datetime.utcnow().isoformat()),
                "quality": payload.get("quality", 100),
                "unit": payload.get("unit"),
                "zone": topic_parts[0] if len(topic_parts) > 0 else None,
                "asset_tag": topic_parts[1] if len(topic_parts) > 1 else None,
                "received_at": datetime.utcnow().isoformat(),
            }

            logger.debug("Received sensor data", sensor_id=sensor_data["sensor_id"])

            # Forward to processing callback
            if self.on_message_callback:
                self.on_message_callback(sensor_data)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in MQTT message", error=str(e), topic=msg.topic)
        except Exception as e:
            logger.error("Error processing MQTT message", error=str(e))

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            logger.info(
                "Connecting to MQTT broker",
                host=self.broker_host,
                port=self.broker_port,
            )
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        except Exception as e:
            logger.error("Failed to connect to MQTT broker", error=str(e))
            raise

    def start(self):
        """Start the MQTT subscriber in a background thread."""
        self.connect()
        self.client.loop_start()
        logger.info("MQTT subscriber started")

    def stop(self):
        """Stop the MQTT subscriber."""
        self.client.loop_stop()
        self.client.disconnect()
        self._is_connected = False
        logger.info("MQTT subscriber stopped")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def publish(self, topic: str, payload: dict, qos: int = 1):
        """Publish a message (for testing or write-back)."""
        self.client.publish(topic, json.dumps(payload), qos=qos)


def create_mqtt_subscriber(callback: Optional[Callable] = None) -> MQTTSubscriber:
    """Factory function to create an MQTT subscriber."""
    return MQTTSubscriber(on_message_callback=callback)

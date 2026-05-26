"""AWS IoT Core integration for secure cloud-based MQTT communication.

Handles device registration, certificate-based authentication,
and bidirectional communication with factory IoT gateways.
"""

import json
import ssl
from datetime import datetime
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AWSIoTCoreClient:
    """
    Client for AWS IoT Core communication.

    Uses X.509 certificate-based mutual TLS authentication
    as required by AWS IoT Core.

    Topics:
        Inbound:  factory/{factory_id}/sensors/{asset_tag}/{sensor_type}
        Outbound: factory/{factory_id}/commands/{asset_tag}
        Shadow:   $aws/things/{thing_name}/shadow/update
    """

    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.endpoint = settings.AWS_IOT_ENDPOINT
        self.cert_path = settings.AWS_IOT_CERT_PATH
        self.key_path = settings.AWS_IOT_KEY_PATH
        self.root_ca_path = settings.AWS_IOT_ROOT_CA_PATH
        self.on_message_callback = on_message_callback
        self._is_connected = False

        # Create MQTT client with TLS
        self.client = mqtt.Client(
            client_id="energy-optimizer-cloud",
            protocol=mqtt.MQTTv311,
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _configure_tls(self):
        """Configure TLS with AWS IoT certificates."""
        self.client.tls_set(
            ca_certs=self.root_ca_path,
            certfile=self.cert_path,
            keyfile=self.key_path,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection to AWS IoT Core."""
        if rc == 0:
            self._is_connected = True
            logger.info("Connected to AWS IoT Core", endpoint=self.endpoint)

            # Subscribe to sensor data topics
            client.subscribe("factory/+/sensors/#", qos=1)
            # Subscribe to device shadow updates
            client.subscribe("$aws/things/+/shadow/update/accepted", qos=1)

            logger.info("Subscribed to AWS IoT Core topics")
        else:
            logger.error("AWS IoT Core connection failed", return_code=rc)

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        self._is_connected = False
        if rc != 0:
            logger.warning("Unexpected AWS IoT Core disconnection", return_code=rc)

    def _on_message(self, client, userdata, msg):
        """Process incoming messages from AWS IoT Core."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))

            message_data = {
                "source": "aws_iot_core",
                "topic": topic,
                "payload": payload,
                "received_at": datetime.utcnow().isoformat(),
            }

            logger.debug("AWS IoT Core message received", topic=topic)

            if self.on_message_callback:
                self.on_message_callback(message_data)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON from AWS IoT Core", error=str(e))
        except Exception as e:
            logger.error("Error processing AWS IoT Core message", error=str(e))

    def connect(self):
        """Connect to AWS IoT Core."""
        if not self.endpoint:
            logger.warning("AWS IoT endpoint not configured, skipping connection")
            return

        try:
            self._configure_tls()
            self.client.connect(self.endpoint, port=8883, keepalive=60)
            logger.info("Connecting to AWS IoT Core", endpoint=self.endpoint)
        except FileNotFoundError as e:
            logger.error("Certificate file not found", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to connect to AWS IoT Core", error=str(e))
            raise

    def start(self):
        """Start the AWS IoT Core client."""
        self.connect()
        self.client.loop_start()
        logger.info("AWS IoT Core client started")

    def stop(self):
        """Stop the AWS IoT Core client."""
        self.client.loop_stop()
        self.client.disconnect()
        self._is_connected = False
        logger.info("AWS IoT Core client stopped")

    def publish_command(self, asset_tag: str, command: dict):
        """Publish a command to a factory asset via AWS IoT Core."""
        topic = f"factory/commands/{asset_tag}"
        payload = {
            "command": command,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "ai_optimizer",
        }
        self.client.publish(topic, json.dumps(payload), qos=1)
        logger.info("Command published to asset", asset_tag=asset_tag, command=command)

    def update_device_shadow(self, thing_name: str, desired_state: dict):
        """Update AWS IoT Device Shadow for a thing."""
        topic = f"$aws/things/{thing_name}/shadow/update"
        payload = {
            "state": {
                "desired": desired_state,
            }
        }
        self.client.publish(topic, json.dumps(payload), qos=1)
        logger.info("Device shadow updated", thing_name=thing_name)

    @property
    def is_connected(self) -> bool:
        return self._is_connected

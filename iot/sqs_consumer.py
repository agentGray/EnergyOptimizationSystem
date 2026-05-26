"""AWS SQS consumer for reliable message processing.

Consumes sensor data messages from SQS queue (populated by AWS IoT Core rules).
Provides reliable, at-least-once delivery with dead-letter queue support.
"""

import json
import time
import threading
from datetime import datetime
from typing import Callable, Optional, List

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQSConsumer:
    """
    AWS SQS consumer for processing sensor data messages.

    AWS IoT Core rules forward sensor messages to SQS for reliable processing.
    This consumer polls the queue and processes messages in batches.

    Message format:
    {
        "sensor_id": "TEMP-001",
        "asset_tag": "chiller-01",
        "value": 72.5,
        "timestamp": "2024-01-15T10:30:00Z",
        "quality": 100,
        "source": "aws_iot_core"
    }
    """

    def __init__(self, on_message_callback: Optional[Callable] = None):
        self.queue_url = settings.SQS_QUEUE_URL
        self.dlq_url = settings.SQS_DEAD_LETTER_QUEUE_URL
        self.on_message_callback = on_message_callback
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Initialize SQS client
        self.sqs_client = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def _poll_messages(self):
        """Continuously poll SQS for messages."""
        logger.info("SQS consumer polling started", queue_url=self.queue_url)

        while self._running:
            try:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,  # Long polling
                    VisibilityTimeout=30,
                    AttributeNames=["All"],
                    MessageAttributeNames=["All"],
                )

                messages = response.get("Messages", [])

                if messages:
                    logger.debug(f"Received {len(messages)} messages from SQS")
                    self._process_batch(messages)

            except ClientError as e:
                logger.error("SQS client error", error=str(e))
                time.sleep(5)
            except Exception as e:
                logger.error("Unexpected error in SQS consumer", error=str(e))
                time.sleep(5)

    def _process_batch(self, messages: List[dict]):
        """Process a batch of SQS messages."""
        successful_receipts = []

        for message in messages:
            try:
                body = json.loads(message["Body"])

                # Handle SNS-wrapped messages
                if "Message" in body:
                    body = json.loads(body["Message"])

                sensor_data = {
                    "source": "sqs",
                    "message_id": message["MessageId"],
                    "sensor_id": body.get("sensor_id"),
                    "asset_tag": body.get("asset_tag"),
                    "value": body.get("value"),
                    "timestamp": body.get("timestamp", datetime.utcnow().isoformat()),
                    "quality": body.get("quality", 100),
                    "received_at": datetime.utcnow().isoformat(),
                }

                # Process message
                if self.on_message_callback:
                    self.on_message_callback(sensor_data)

                successful_receipts.append(
                    {
                        "Id": message["MessageId"],
                        "ReceiptHandle": message["ReceiptHandle"],
                    }
                )

            except json.JSONDecodeError as e:
                logger.error(
                    "Invalid JSON in SQS message",
                    message_id=message["MessageId"],
                    error=str(e),
                )
            except Exception as e:
                logger.error(
                    "Error processing SQS message",
                    message_id=message["MessageId"],
                    error=str(e),
                )

        # Delete successfully processed messages
        if successful_receipts:
            self._delete_messages(successful_receipts)

    def _delete_messages(self, receipts: List[dict]):
        """Delete processed messages from SQS."""
        try:
            response = self.sqs_client.delete_message_batch(
                QueueUrl=self.queue_url,
                Entries=receipts,
            )
            failed = response.get("Failed", [])
            if failed:
                logger.warning(f"Failed to delete {len(failed)} messages from SQS")
        except ClientError as e:
            logger.error("Error deleting SQS messages", error=str(e))

    def start(self):
        """Start the SQS consumer in a background thread."""
        if not self.queue_url:
            logger.warning("SQS queue URL not configured, skipping consumer start")
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll_messages, daemon=True)
        self._thread.start()
        logger.info("SQS consumer started")

    def stop(self):
        """Stop the SQS consumer."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=30)
        logger.info("SQS consumer stopped")

    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=[
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                    "ApproximateNumberOfMessagesDelayed",
                ],
            )
            attrs = response.get("Attributes", {})
            return {
                "messages_available": int(attrs.get("ApproximateNumberOfMessages", 0)),
                "messages_in_flight": int(
                    attrs.get("ApproximateNumberOfMessagesNotVisible", 0)
                ),
                "messages_delayed": int(
                    attrs.get("ApproximateNumberOfMessagesDelayed", 0)
                ),
            }
        except ClientError as e:
            logger.error("Error getting queue stats", error=str(e))
            return {}

    @property
    def is_running(self) -> bool:
        return self._running

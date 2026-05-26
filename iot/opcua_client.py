"""OPC-UA client for SCADA system communication.

Connects to OPC-UA servers on SCADA systems to read sensor values
and write control commands back to industrial equipment.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OPCUAClient:
    """
    OPC-UA client for industrial SCADA communication.

    Provides:
    - Reading sensor values from OPC-UA nodes
    - Writing setpoints and commands back to SCADA
    - Subscribing to value changes for real-time monitoring
    - Browsing available nodes on the OPC-UA server
    """

    def __init__(self):
        self.server_url = f"opc.tcp://{settings.SCADA_HOST}:{settings.SCADA_PORT}"
        self.username = settings.SCADA_USERNAME
        self.password = settings.SCADA_PASSWORD
        self._client = None
        self._is_connected = False
        self._subscriptions: Dict[str, Any] = {}

    async def connect(self):
        """Connect to the OPC-UA server."""
        try:
            from asyncua import Client as AsyncOPCUAClient

            self._client = AsyncOPCUAClient(url=self.server_url)
            self._client.set_user(self.username)
            self._client.set_password(self.password)

            await self._client.connect()
            self._is_connected = True
            logger.info("Connected to OPC-UA server", url=self.server_url)
        except ImportError:
            logger.warning("asyncua not installed, OPC-UA client unavailable")
        except Exception as e:
            logger.error("Failed to connect to OPC-UA server", error=str(e))
            raise

    async def disconnect(self):
        """Disconnect from the OPC-UA server."""
        if self._client and self._is_connected:
            await self._client.disconnect()
            self._is_connected = False
            logger.info("Disconnected from OPC-UA server")

    async def read_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a value from an OPC-UA node.

        Args:
            node_id: OPC-UA node identifier (e.g., "ns=2;i=1001")

        Returns:
            Dictionary with value, timestamp, and quality info
        """
        if not self._is_connected:
            logger.error("Not connected to OPC-UA server")
            return None

        try:
            node = self._client.get_node(node_id)
            value = await node.read_value()
            data_value = await node.read_data_value()

            return {
                "node_id": node_id,
                "value": value,
                "timestamp": data_value.SourceTimestamp or datetime.utcnow(),
                "quality": str(data_value.StatusCode),
                "source": "opcua",
            }
        except Exception as e:
            logger.error("Error reading OPC-UA node", node_id=node_id, error=str(e))
            return None

    async def read_nodes(self, node_ids: List[str]) -> List[Dict[str, Any]]:
        """Read values from multiple OPC-UA nodes."""
        results = []
        for node_id in node_ids:
            result = await self.read_node(node_id)
            if result:
                results.append(result)
        return results

    async def write_node(self, node_id: str, value: Any) -> bool:
        """
        Write a value to an OPC-UA node (SCADA write-back).

        Args:
            node_id: OPC-UA node identifier
            value: Value to write

        Returns:
            True if write was successful
        """
        if not self._is_connected:
            logger.error("Not connected to OPC-UA server")
            return False

        if not settings.SCADA_WRITEBACK_ENABLED:
            logger.warning("SCADA write-back is disabled")
            return False

        try:
            node = self._client.get_node(node_id)
            await node.write_value(value)
            logger.info(
                "Written value to OPC-UA node",
                node_id=node_id,
                value=value,
            )
            return True
        except Exception as e:
            logger.error(
                "Error writing to OPC-UA node",
                node_id=node_id,
                value=value,
                error=str(e),
            )
            return False

    async def browse_nodes(self, parent_node_id: str = "i=85") -> List[Dict[str, str]]:
        """
        Browse available nodes on the OPC-UA server.

        Args:
            parent_node_id: Parent node to browse from (default: Objects folder)

        Returns:
            List of child nodes with their IDs and names
        """
        if not self._is_connected:
            return []

        try:
            node = self._client.get_node(parent_node_id)
            children = await node.get_children()

            results = []
            for child in children:
                name = await child.read_browse_name()
                results.append(
                    {
                        "node_id": str(child.nodeid),
                        "name": name.Name,
                        "namespace": name.NamespaceIndex,
                    }
                )
            return results
        except Exception as e:
            logger.error("Error browsing OPC-UA nodes", error=str(e))
            return []

    async def subscribe_to_changes(
        self, node_ids: List[str], callback: Any, interval_ms: int = 1000
    ):
        """
        Subscribe to value changes on OPC-UA nodes.

        Args:
            node_ids: List of node IDs to monitor
            callback: Async callback function for value changes
            interval_ms: Subscription interval in milliseconds
        """
        if not self._is_connected:
            logger.error("Not connected to OPC-UA server")
            return

        try:
            subscription = await self._client.create_subscription(interval_ms, callback)
            nodes = [self._client.get_node(nid) for nid in node_ids]
            await subscription.subscribe_data_change(nodes)
            self._subscriptions[str(node_ids)] = subscription
            logger.info(
                "Subscribed to OPC-UA node changes",
                node_count=len(node_ids),
                interval_ms=interval_ms,
            )
        except Exception as e:
            logger.error("Error subscribing to OPC-UA changes", error=str(e))

    @property
    def is_connected(self) -> bool:
        return self._is_connected

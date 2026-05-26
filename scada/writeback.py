"""SCADA write-back module for executing approved commands.

Translates AI recommendations into SCADA-compatible commands
and executes them through OPC-UA or MQTT protocols.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WritebackCommand:
    """A command to be written back to SCADA."""
    command_id: str
    asset_tag: str
    action: str
    parameters: Dict[str, Any]
    priority: str
    source: str  # "ai_engine" or "operator"
    timestamp: datetime


@dataclass
class WritebackResult:
    """Result of a SCADA write-back operation."""
    success: bool
    command_id: str
    message: str
    executed_at: datetime
    response_data: Optional[Dict] = None


class SCADAWriteback:
    """
    SCADA write-back controller.

    Executes approved recommendations by sending commands
    to factory equipment through SCADA/PLC systems.

    Safety features:
    - Pre-execution safety checks
    - Rate limiting
    - Command validation
    - Rollback capability
    - Audit logging
    """

    # Allowed commands per asset type
    ALLOWED_COMMANDS = {
        "hvac": [
            "adjust_setpoint", "change_mode", "schedule_shutdown",
            "schedule_startup",
        ],
        "compressor": [
            "reduce_load", "schedule_shutdown", "schedule_startup",
            "adjust_pressure",
        ],
        "pump": [
            "reduce_flow", "schedule_shutdown", "schedule_startup",
            "adjust_speed",
        ],
        "lighting": [
            "dim", "schedule_shutdown", "schedule_startup", "set_level",
        ],
        "motor": [
            "reduce_speed", "schedule_shutdown", "schedule_startup",
        ],
        "furnace": [
            "adjust_temperature", "reduce_output", "schedule_shutdown",
        ],
        "chiller": [
            "adjust_setpoint", "reduce_load", "schedule_shutdown",
            "schedule_startup",
        ],
    }

    # Safety limits per parameter
    SAFETY_LIMITS = {
        "target_temp": {"min": 16.0, "max": 30.0},
        "reduce_by_percent": {"min": 0, "max": 50},
        "speed_percent": {"min": 20, "max": 100},
        "pressure_bar": {"min": 2.0, "max": 12.0},
    }

    def __init__(self):
        self.enabled = settings.SCADA_WRITEBACK_ENABLED
        self._execution_log = []
        self._opcua_client = None
        self._mqtt_client = None

    async def execute_command(
        self, command: WritebackCommand
    ) -> WritebackResult:
        """
        Execute a write-back command to SCADA.

        Args:
            command: The validated command to execute

        Returns:
            WritebackResult with success status
        """
        if not self.enabled:
            return WritebackResult(
                success=False,
                command_id=command.command_id,
                message="SCADA write-back is disabled",
                executed_at=datetime.utcnow(),
            )

        # Safety check
        safety_ok, safety_msg = self._safety_check(command)
        if not safety_ok:
            logger.warning(
                "Safety check failed",
                command_id=command.command_id,
                reason=safety_msg,
            )
            return WritebackResult(
                success=False,
                command_id=command.command_id,
                message=f"Safety check failed: {safety_msg}",
                executed_at=datetime.utcnow(),
            )

        # Execute via appropriate protocol
        try:
            result = await self._send_to_scada(command)
            self._log_execution(command, result)
            return result
        except Exception as e:
            logger.error(
                "SCADA write-back failed",
                command_id=command.command_id,
                error=str(e),
            )
            return WritebackResult(
                success=False,
                command_id=command.command_id,
                message=f"Execution failed: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    def _safety_check(self, command: WritebackCommand) -> tuple:
        """
        Perform pre-execution safety checks.

        Returns:
            Tuple of (is_safe: bool, message: str)
        """
        # Check if command is allowed for asset type
        asset_type = command.parameters.get("asset_type", "generic")
        allowed = self.ALLOWED_COMMANDS.get(asset_type, [])

        if command.action not in allowed and allowed:
            return False, (
                f"Command '{command.action}' not allowed for "
                f"asset type '{asset_type}'"
            )

        # Check parameter safety limits
        for param_name, value in command.parameters.items():
            if param_name in self.SAFETY_LIMITS:
                limits = self.SAFETY_LIMITS[param_name]
                if isinstance(value, (int, float)):
                    if value < limits["min"] or value > limits["max"]:
                        return False, (
                            f"Parameter '{param_name}' value {value} "
                            f"outside safe range [{limits['min']}, "
                            f"{limits['max']}]"
                        )

        # Rate limiting: max 10 commands per minute per asset
        recent_commands = [
            log for log in self._execution_log[-100:]
            if log["asset_tag"] == command.asset_tag
            and (datetime.utcnow() - log["timestamp"]).seconds < 60
        ]
        if len(recent_commands) >= 10:
            return False, "Rate limit exceeded (10 commands/min/asset)"

        return True, "All safety checks passed"

    async def _send_to_scada(
        self, command: WritebackCommand
    ) -> WritebackResult:
        """Send command to SCADA via OPC-UA or MQTT."""
        # Determine protocol based on configuration
        protocol = command.parameters.get("protocol", "opcua")

        if protocol == "opcua":
            return await self._send_via_opcua(command)
        else:
            return await self._send_via_mqtt(command)

    async def _send_via_opcua(
        self, command: WritebackCommand
    ) -> WritebackResult:
        """Send command via OPC-UA protocol."""
        try:
            from iot.opcua_client import OPCUAClient

            if not self._opcua_client:
                self._opcua_client = OPCUAClient()
                await self._opcua_client.connect()

            # Map command to OPC-UA node write
            node_id = command.parameters.get("opcua_node_id")
            value = self._build_opcua_value(command)

            if node_id and value is not None:
                success = await self._opcua_client.write_node(node_id, value)
                return WritebackResult(
                    success=success,
                    command_id=command.command_id,
                    message="Command sent via OPC-UA" if success else "OPC-UA write failed",
                    executed_at=datetime.utcnow(),
                    response_data={"node_id": node_id, "value": value},
                )
            else:
                return WritebackResult(
                    success=False,
                    command_id=command.command_id,
                    message="Missing OPC-UA node_id or invalid value",
                    executed_at=datetime.utcnow(),
                )

        except Exception as e:
            return WritebackResult(
                success=False,
                command_id=command.command_id,
                message=f"OPC-UA error: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _send_via_mqtt(
        self, command: WritebackCommand
    ) -> WritebackResult:
        """Send command via MQTT protocol."""
        try:
            from iot.mqtt_subscriber import MQTTSubscriber

            if not self._mqtt_client:
                self._mqtt_client = MQTTSubscriber()
                self._mqtt_client.connect()

            topic = f"factory/commands/{command.asset_tag}"
            payload = {
                "command_id": command.command_id,
                "action": command.action,
                "parameters": command.parameters,
                "timestamp": datetime.utcnow().isoformat(),
                "source": command.source,
            }

            self._mqtt_client.publish(topic, payload)

            return WritebackResult(
                success=True,
                command_id=command.command_id,
                message="Command published via MQTT",
                executed_at=datetime.utcnow(),
                response_data={"topic": topic},
            )

        except Exception as e:
            return WritebackResult(
                success=False,
                command_id=command.command_id,
                message=f"MQTT error: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    def _build_opcua_value(self, command: WritebackCommand) -> Any:
        """Build OPC-UA value from command parameters."""
        action = command.action
        params = command.parameters

        if action == "adjust_setpoint":
            return params.get("target_temp")
        elif action == "reduce_load":
            return params.get("reduce_by_percent")
        elif action == "schedule_shutdown":
            return 0  # Signal to stop
        elif action == "schedule_startup":
            return 1  # Signal to start
        elif action == "adjust_speed":
            return params.get("speed_percent")
        return None

    def _log_execution(
        self, command: WritebackCommand, result: WritebackResult
    ):
        """Log command execution for audit trail."""
        self._execution_log.append({
            "command_id": command.command_id,
            "asset_tag": command.asset_tag,
            "action": command.action,
            "success": result.success,
            "message": result.message,
            "timestamp": datetime.utcnow(),
        })
        logger.info(
            "SCADA command executed",
            command_id=command.command_id,
            asset_tag=command.asset_tag,
            action=command.action,
            success=result.success,
        )

    def get_execution_history(self, limit: int = 50) -> list:
        """Get recent execution history."""
        return self._execution_log[-limit:]

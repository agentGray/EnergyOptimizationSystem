"""Anomaly model for detected energy waste patterns."""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text
from app.core.database import Base


class AnomalyType(str, enum.Enum):
    PHANTOM_LOAD = "phantom_load"
    HVAC_OVERCOOLING = "hvac_overcooling"
    AIR_LEAK = "air_leak"
    VOLTAGE_IMBALANCE = "voltage_imbalance"
    FURNACE_CYCLING = "furnace_cycling"
    MOTOR_OVERLOAD = "motor_overload"
    POWER_SPIKE = "power_spike"
    EFFICIENCY_DROP = "efficiency_drop"
    UNUSUAL_PATTERN = "unusual_pattern"
    EQUIPMENT_DEGRADATION = "equipment_degradation"


class AnomalySeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Anomaly(Base):
    """Detected energy anomaly or waste pattern."""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    anomaly_type = Column(Enum(AnomalyType), nullable=False)
    severity = Column(Enum(AnomalySeverity), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False)
    energy_waste_kwh = Column(Float)  # Estimated energy wasted
    cost_impact_usd = Column(Float)  # Estimated cost impact
    root_cause = Column(Text)
    affected_sensors = Column(String(500))  # Comma-separated sensor IDs
    baseline_value = Column(Float)
    actual_value = Column(Float)
    deviation_percent = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<Anomaly(id={self.id}, type='{self.anomaly_type}', "
            f"severity='{self.severity}', asset_id={self.asset_id})>"
        )

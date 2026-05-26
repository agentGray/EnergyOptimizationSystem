"""Sensor model for industrial measurement devices."""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class SensorType(str, enum.Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VOLTAGE = "voltage"
    CURRENT = "current"
    POWER = "power"
    ENERGY = "energy"
    FLOW_RATE = "flow_rate"
    VIBRATION = "vibration"
    HUMIDITY = "humidity"
    RPM = "rpm"
    CO2 = "co2"
    POWER_FACTOR = "power_factor"


class SensorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAULTY = "faulty"
    CALIBRATING = "calibrating"


class Sensor(Base):
    """Industrial sensor attached to an asset."""

    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sensor_type = Column(Enum(SensorType), nullable=False)
    unit = Column(String(50), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    status = Column(Enum(SensorStatus), default=SensorStatus.ACTIVE)
    min_value = Column(Float)
    max_value = Column(Float)
    accuracy = Column(Float)
    sampling_rate_seconds = Column(Integer, default=5)
    mqtt_topic = Column(String(255))
    opcua_node_id = Column(String(255))
    is_virtual = Column(Boolean, default=False)
    calibration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id={self.id}, sensor_id='{self.sensor_id}', type='{self.sensor_type}')>"

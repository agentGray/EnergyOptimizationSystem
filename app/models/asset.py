"""Asset model representing factory machines and equipment."""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class AssetType(str, enum.Enum):
    CHILLER = "chiller"
    HVAC = "hvac"
    COMPRESSOR = "compressor"
    FURNACE = "furnace"
    PUMP = "pump"
    LIGHTING = "lighting"
    MOTOR = "motor"
    BOILER = "boiler"
    TRANSFORMER = "transformer"
    CONVEYOR = "conveyor"


class AssetStatus(str, enum.Enum):
    RUNNING = "running"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    FAULT = "fault"


class Asset(Base):
    """Factory machine or equipment asset."""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    asset_tag = Column(String(100), unique=True, index=True, nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    status = Column(Enum(AssetStatus), default=AssetStatus.OFFLINE)
    location = Column(String(255))
    zone = Column(String(100))
    manufacturer = Column(String(255))
    model_number = Column(String(100))
    serial_number = Column(String(100))
    rated_power_kw = Column(Float, nullable=False)
    nominal_voltage = Column(Float)
    nominal_current = Column(Float)
    efficiency_rating = Column(Float)
    installation_date = Column(DateTime)
    last_maintenance_date = Column(DateTime)
    description = Column(Text)
    is_critical = Column(Boolean, default=False)
    health_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensors = relationship("Sensor", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.asset_type}')>"

"""Sensor reading model for time-series data (TimescaleDB hypertable)."""

from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class SensorReading(Base):
    """
    Time-series sensor reading.
    
    This table is designed to be a TimescaleDB hypertable partitioned by timestamp.
    Run the following SQL after table creation:
    
        SELECT create_hypertable('sensor_readings', 'timestamp');
    """

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    value = Column(Float, nullable=False)
    quality = Column(Integer, default=100)  # Data quality score 0-100
    source = Column(String(50), default="mqtt")  # mqtt, opcua, manual, simulated

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")

    # Composite index for efficient time-range queries
    __table_args__ = (
        Index("idx_sensor_readings_sensor_time", "sensor_id", "timestamp"),
        Index("idx_sensor_readings_timestamp", "timestamp"),
    )

    def __repr__(self):
        return (
            f"<SensorReading(sensor_id={self.sensor_id}, "
            f"timestamp='{self.timestamp}', value={self.value})>"
        )

"""Service layer for sensor and reading operations."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.sensor import Sensor
from app.models.reading import SensorReading
from app.schemas.sensor import SensorCreate, SensorUpdate, SensorReadingCreate


class SensorService:
    """Service for managing sensors and readings."""

    def __init__(self, db: Session):
        self.db = db

    def create_sensor(self, sensor_data: SensorCreate) -> Sensor:
        """Create a new sensor."""
        sensor = Sensor(**sensor_data.model_dump())
        self.db.add(sensor)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def get_sensor(self, sensor_id: int) -> Optional[Sensor]:
        """Get a sensor by ID."""
        return self.db.query(Sensor).filter(Sensor.id == sensor_id).first()

    def get_sensor_by_sensor_id(self, sensor_id_str: str) -> Optional[Sensor]:
        """Get a sensor by its string identifier."""
        return self.db.query(Sensor).filter(Sensor.sensor_id == sensor_id_str).first()

    def list_sensors(
        self,
        skip: int = 0,
        limit: int = 100,
        asset_id: Optional[int] = None,
    ) -> List[Sensor]:
        """List sensors with optional filters."""
        query = self.db.query(Sensor)
        if asset_id:
            query = query.filter(Sensor.asset_id == asset_id)
        return query.offset(skip).limit(limit).all()

    def update_sensor(self, sensor_id: int, sensor_data: SensorUpdate) -> Optional[Sensor]:
        """Update a sensor."""
        sensor = self.get_sensor(sensor_id)
        if not sensor:
            return None
        update_data = sensor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sensor, field, value)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def delete_sensor(self, sensor_id: int) -> bool:
        """Delete a sensor."""
        sensor = self.get_sensor(sensor_id)
        if not sensor:
            return False
        self.db.delete(sensor)
        self.db.commit()
        return True

    def ingest_reading(self, reading_data: SensorReadingCreate) -> SensorReading:
        """Ingest a single sensor reading."""
        reading = SensorReading(
            sensor_id=reading_data.sensor_id,
            value=reading_data.value,
            timestamp=reading_data.timestamp or datetime.utcnow(),
            quality=reading_data.quality,
            source=reading_data.source,
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def ingest_batch(self, readings: List[SensorReadingCreate]) -> int:
        """Ingest a batch of sensor readings. Returns count of ingested readings."""
        objects = []
        for r in readings:
            objects.append(
                SensorReading(
                    sensor_id=r.sensor_id,
                    value=r.value,
                    timestamp=r.timestamp or datetime.utcnow(),
                    quality=r.quality,
                    source=r.source,
                )
            )
        self.db.bulk_save_objects(objects)
        self.db.commit()
        return len(objects)

    def get_readings(
        self,
        sensor_id: int,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[SensorReading]:
        """Get readings for a sensor within a time range."""
        return (
            self.db.query(SensorReading)
            .filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time,
            )
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_latest_reading(self, sensor_id: int) -> Optional[SensorReading]:
        """Get the most recent reading for a sensor."""
        return (
            self.db.query(SensorReading)
            .filter(SensorReading.sensor_id == sensor_id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )

    def get_sensor_stats(
        self, sensor_id: int, start_time: datetime, end_time: datetime
    ) -> dict:
        """Get statistical summary of sensor readings."""
        result = (
            self.db.query(
                func.avg(SensorReading.value).label("avg"),
                func.min(SensorReading.value).label("min"),
                func.max(SensorReading.value).label("max"),
                func.count(SensorReading.id).label("count"),
            )
            .filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time,
            )
            .first()
        )
        return {
            "avg": round(result.avg, 4) if result.avg else 0,
            "min": round(result.min, 4) if result.min else 0,
            "max": round(result.max, 4) if result.max else 0,
            "count": result.count or 0,
        }

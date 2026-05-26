"""Pydantic schemas for Sensor and SensorReading endpoints."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.sensor import SensorType, SensorStatus


class SensorBase(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    sensor_type: SensorType
    unit: str = Field(..., min_length=1, max_length=50)
    asset_id: int
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    accuracy: Optional[float] = None
    sampling_rate_seconds: int = 5
    mqtt_topic: Optional[str] = None
    opcua_node_id: Optional[str] = None
    is_virtual: bool = False


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[SensorStatus] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    sampling_rate_seconds: Optional[int] = None
    mqtt_topic: Optional[str] = None
    opcua_node_id: Optional[str] = None


class SensorResponse(SensorBase):
    id: int
    status: SensorStatus
    calibration_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    sensor_id: int
    value: float
    timestamp: Optional[datetime] = None
    quality: int = Field(100, ge=0, le=100)
    source: str = "mqtt"


class SensorReadingBatch(BaseModel):
    readings: List[SensorReadingCreate]


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: int
    timestamp: datetime
    value: float
    quality: int
    source: str

    class Config:
        from_attributes = True


class SensorDataQuery(BaseModel):
    sensor_id: int
    start_time: datetime
    end_time: datetime
    aggregation: Optional[str] = None  # avg, min, max, sum
    interval: Optional[str] = None  # 1m, 5m, 1h, 1d

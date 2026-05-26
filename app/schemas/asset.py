"""Pydantic schemas for Asset endpoints."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.asset import AssetType, AssetStatus


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_tag: str = Field(..., min_length=1, max_length=100)
    asset_type: AssetType
    location: Optional[str] = None
    zone: Optional[str] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    rated_power_kw: float = Field(..., gt=0)
    nominal_voltage: Optional[float] = None
    nominal_current: Optional[float] = None
    efficiency_rating: Optional[float] = Field(None, ge=0, le=1)
    description: Optional[str] = None
    is_critical: bool = False


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[AssetStatus] = None
    location: Optional[str] = None
    zone: Optional[str] = None
    rated_power_kw: Optional[float] = None
    efficiency_rating: Optional[float] = None
    description: Optional[str] = None
    is_critical: Optional[bool] = None
    health_score: Optional[float] = Field(None, ge=0, le=100)


class AssetResponse(AssetBase):
    id: int
    status: AssetStatus
    health_score: float
    installation_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetSummary(BaseModel):
    total_assets: int
    running: int
    idle: int
    maintenance: int
    offline: int
    fault: int
    avg_health_score: float
    total_rated_power_kw: float

"""Pydantic schemas for Recommendation endpoints."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.recommendation import (
    RecommendationStatus,
    RecommendationPriority,
    RecommendationCategory,
)


class RecommendationCreate(BaseModel):
    asset_id: int
    anomaly_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    category: RecommendationCategory
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    estimated_savings_kwh: Optional[float] = None
    estimated_savings_usd: Optional[float] = None
    estimated_co2_reduction_kg: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    action_command: Optional[str] = None
    action_parameters: Optional[str] = None
    requires_approval: bool = True


class RecommendationResponse(BaseModel):
    id: int
    asset_id: int
    anomaly_id: Optional[int]
    title: str
    description: str
    category: RecommendationCategory
    priority: RecommendationPriority
    status: RecommendationStatus
    estimated_savings_kwh: Optional[float]
    estimated_savings_usd: Optional[float]
    estimated_co2_reduction_kg: Optional[float]
    confidence_score: Optional[float]
    action_command: Optional[str]
    requires_approval: bool
    approved_at: Optional[datetime]
    executed_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecommendationApproval(BaseModel):
    approved: bool
    reason: Optional[str] = None


class RecommendationSummary(BaseModel):
    total_recommendations: int
    pending: int
    approved: int
    executed: int
    rejected: int
    total_estimated_savings_kwh: float
    total_estimated_savings_usd: float
    total_co2_reduction_kg: float

"""Service layer for recommendation operations."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.recommendation import Recommendation, RecommendationStatus
from app.schemas.recommendation import RecommendationCreate, RecommendationSummary


class RecommendationService:
    """Service for managing AI-generated recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def create_recommendation(self, data: RecommendationCreate) -> Recommendation:
        """Create a new recommendation."""
        rec = Recommendation(**data.model_dump())
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_recommendation(self, rec_id: int) -> Optional[Recommendation]:
        """Get a recommendation by ID."""
        return self.db.query(Recommendation).filter(Recommendation.id == rec_id).first()

    def list_recommendations(
        self,
        skip: int = 0,
        limit: int = 100,
        asset_id: Optional[int] = None,
        status: Optional[RecommendationStatus] = None,
    ) -> List[Recommendation]:
        """List recommendations with optional filters."""
        query = self.db.query(Recommendation)
        if asset_id:
            query = query.filter(Recommendation.asset_id == asset_id)
        if status:
            query = query.filter(Recommendation.status == status)
        return query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()

    def approve_recommendation(
        self, rec_id: int, user_id: int, reason: Optional[str] = None
    ) -> Optional[Recommendation]:
        """Approve a recommendation for execution."""
        rec = self.get_recommendation(rec_id)
        if not rec or rec.status != RecommendationStatus.PENDING:
            return None
        rec.status = RecommendationStatus.APPROVED
        rec.approved_by = user_id
        rec.approved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def reject_recommendation(
        self, rec_id: int, reason: Optional[str] = None
    ) -> Optional[Recommendation]:
        """Reject a recommendation."""
        rec = self.get_recommendation(rec_id)
        if not rec or rec.status != RecommendationStatus.PENDING:
            return None
        rec.status = RecommendationStatus.REJECTED
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def mark_executed(self, rec_id: int) -> Optional[Recommendation]:
        """Mark a recommendation as executed."""
        rec = self.get_recommendation(rec_id)
        if not rec or rec.status != RecommendationStatus.APPROVED:
            return None
        rec.status = RecommendationStatus.EXECUTED
        rec.executed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_summary(self) -> RecommendationSummary:
        """Get recommendation summary statistics."""
        total = self.db.query(func.count(Recommendation.id)).scalar() or 0
        pending = (
            self.db.query(func.count(Recommendation.id))
            .filter(Recommendation.status == RecommendationStatus.PENDING)
            .scalar() or 0
        )
        approved = (
            self.db.query(func.count(Recommendation.id))
            .filter(Recommendation.status == RecommendationStatus.APPROVED)
            .scalar() or 0
        )
        executed = (
            self.db.query(func.count(Recommendation.id))
            .filter(Recommendation.status == RecommendationStatus.EXECUTED)
            .scalar() or 0
        )
        rejected = (
            self.db.query(func.count(Recommendation.id))
            .filter(Recommendation.status == RecommendationStatus.REJECTED)
            .scalar() or 0
        )
        total_savings_kwh = (
            self.db.query(func.sum(Recommendation.estimated_savings_kwh))
            .filter(Recommendation.status == RecommendationStatus.EXECUTED)
            .scalar() or 0.0
        )
        total_savings_usd = (
            self.db.query(func.sum(Recommendation.estimated_savings_usd))
            .filter(Recommendation.status == RecommendationStatus.EXECUTED)
            .scalar() or 0.0
        )
        total_co2 = (
            self.db.query(func.sum(Recommendation.estimated_co2_reduction_kg))
            .filter(Recommendation.status == RecommendationStatus.EXECUTED)
            .scalar() or 0.0
        )

        return RecommendationSummary(
            total_recommendations=total,
            pending=pending,
            approved=approved,
            executed=executed,
            rejected=rejected,
            total_estimated_savings_kwh=round(total_savings_kwh, 2),
            total_estimated_savings_usd=round(total_savings_usd, 2),
            total_co2_reduction_kg=round(total_co2, 2),
        )

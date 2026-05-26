"""API routes for recommendation management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.recommendation import RecommendationStatus
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationApproval,
    RecommendationSummary,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse, status_code=201)
def create_recommendation(data: RecommendationCreate, db: Session = Depends(get_db)):
    """Create a new recommendation (typically called by AI engine)."""
    service = RecommendationService(db)
    return service.create_recommendation(data)


@router.get("/", response_model=List[RecommendationResponse])
def list_recommendations(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    status: Optional[RecommendationStatus] = None,
    db: Session = Depends(get_db),
):
    """List recommendations with optional filters."""
    service = RecommendationService(db)
    return service.list_recommendations(skip=skip, limit=limit, asset_id=asset_id, status=status)


@router.get("/summary", response_model=RecommendationSummary)
def get_recommendation_summary(db: Session = Depends(get_db)):
    """Get recommendation summary statistics."""
    service = RecommendationService(db)
    return service.get_summary()


@router.get("/{rec_id}", response_model=RecommendationResponse)
def get_recommendation(rec_id: int, db: Session = Depends(get_db)):
    """Get a specific recommendation by ID."""
    service = RecommendationService(db)
    rec = service.get_recommendation(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.post("/{rec_id}/approve", response_model=RecommendationResponse)
def approve_recommendation(
    rec_id: int,
    approval: RecommendationApproval,
    db: Session = Depends(get_db),
):
    """Approve or reject a recommendation."""
    service = RecommendationService(db)
    if approval.approved:
        # TODO: Get actual user_id from auth context
        rec = service.approve_recommendation(rec_id, user_id=1, reason=approval.reason)
    else:
        rec = service.reject_recommendation(rec_id, reason=approval.reason)
    if not rec:
        raise HTTPException(
            status_code=400, detail="Recommendation not found or not in pending status"
        )
    return rec


@router.post("/{rec_id}/execute", response_model=RecommendationResponse)
def execute_recommendation(rec_id: int, db: Session = Depends(get_db)):
    """Mark a recommendation as executed (after SCADA write-back)."""
    service = RecommendationService(db)
    rec = service.mark_executed(rec_id)
    if not rec:
        raise HTTPException(
            status_code=400, detail="Recommendation not found or not approved"
        )
    return rec

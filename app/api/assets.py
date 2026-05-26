"""API routes for asset management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetSummary
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/", response_model=AssetResponse, status_code=201)
def create_asset(asset_data: AssetCreate, db: Session = Depends(get_db)):
    """Create a new factory asset."""
    service = AssetService(db)
    existing = service.get_asset_by_tag(asset_data.asset_tag)
    if existing:
        raise HTTPException(status_code=400, detail="Asset tag already exists")
    return service.create_asset(asset_data)


@router.get("/", response_model=List[AssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[AssetStatus] = None,
    zone: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all assets with optional filters."""
    service = AssetService(db)
    return service.list_assets(skip=skip, limit=limit, status=status, zone=zone)


@router.get("/summary", response_model=AssetSummary)
def get_asset_summary(db: Session = Depends(get_db)):
    """Get summary statistics of all assets."""
    service = AssetService(db)
    return service.get_summary()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get a specific asset by ID."""
    service = AssetService(db)
    asset = service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset_data: AssetUpdate, db: Session = Depends(get_db)):
    """Update an existing asset."""
    service = AssetService(db)
    asset = service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete an asset."""
    service = AssetService(db)
    if not service.delete_asset(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")

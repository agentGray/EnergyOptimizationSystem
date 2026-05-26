"""Service layer for asset operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import Asset, AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate, AssetSummary


class AssetService:
    """Service for managing factory assets."""

    def __init__(self, db: Session):
        self.db = db

    def create_asset(self, asset_data: AssetCreate) -> Asset:
        """Create a new asset."""
        asset = Asset(**asset_data.model_dump())
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_asset(self, asset_id: int) -> Optional[Asset]:
        """Get an asset by ID."""
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def get_asset_by_tag(self, asset_tag: str) -> Optional[Asset]:
        """Get an asset by its tag."""
        return self.db.query(Asset).filter(Asset.asset_tag == asset_tag).first()

    def list_assets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AssetStatus] = None,
        zone: Optional[str] = None,
    ) -> List[Asset]:
        """List assets with optional filters."""
        query = self.db.query(Asset)
        if status:
            query = query.filter(Asset.status == status)
        if zone:
            query = query.filter(Asset.zone == zone)
        return query.offset(skip).limit(limit).all()

    def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> Optional[Asset]:
        """Update an asset."""
        asset = self.get_asset(asset_id)
        if not asset:
            return None
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset."""
        asset = self.get_asset(asset_id)
        if not asset:
            return False
        self.db.delete(asset)
        self.db.commit()
        return True

    def get_summary(self) -> AssetSummary:
        """Get a summary of all assets."""
        total = self.db.query(func.count(Asset.id)).scalar() or 0
        running = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.status == AssetStatus.RUNNING)
            .scalar() or 0
        )
        idle = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.status == AssetStatus.IDLE)
            .scalar() or 0
        )
        maintenance = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.status == AssetStatus.MAINTENANCE)
            .scalar() or 0
        )
        offline = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.status == AssetStatus.OFFLINE)
            .scalar() or 0
        )
        fault = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.status == AssetStatus.FAULT)
            .scalar() or 0
        )
        avg_health = self.db.query(func.avg(Asset.health_score)).scalar() or 0.0
        total_power = self.db.query(func.sum(Asset.rated_power_kw)).scalar() or 0.0

        return AssetSummary(
            total_assets=total,
            running=running,
            idle=idle,
            maintenance=maintenance,
            offline=offline,
            fault=fault,
            avg_health_score=round(avg_health, 2),
            total_rated_power_kw=round(total_power, 2),
        )

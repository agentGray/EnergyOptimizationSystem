"""API routes for dashboard data."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.asset import Asset, AssetStatus
from app.models.anomaly import Anomaly
from app.models.recommendation import Recommendation, RecommendationStatus
from app.schemas.dashboard import DashboardOverview, ESGMetrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get main dashboard overview metrics."""
    active_assets = (
        db.query(func.count(Asset.id)).filter(Asset.status == AssetStatus.RUNNING).scalar() or 0
    )
    active_anomalies = (
        db.query(func.count(Anomaly.id)).filter(Anomaly.is_resolved == False).scalar() or 0
    )
    pending_recs = (
        db.query(func.count(Recommendation.id))
        .filter(Recommendation.status == RecommendationStatus.PENDING)
        .scalar() or 0
    )
    total_rated_power = (
        db.query(func.sum(Asset.rated_power_kw))
        .filter(Asset.status == AssetStatus.RUNNING)
        .scalar() or 0.0
    )
    savings_kwh = (
        db.query(func.sum(Recommendation.estimated_savings_kwh))
        .filter(Recommendation.status == RecommendationStatus.EXECUTED)
        .scalar() or 0.0
    )
    co2_reduction = (
        db.query(func.sum(Recommendation.estimated_co2_reduction_kg))
        .filter(Recommendation.status == RecommendationStatus.EXECUTED)
        .scalar() or 0.0
    )

    return DashboardOverview(
        total_power_kw=round(total_rated_power * 0.7, 2),  # Estimate actual from rated
        total_energy_today_kwh=round(total_rated_power * 0.7 * 8, 2),  # 8 hours estimate
        total_cost_today_usd=round(total_rated_power * 0.7 * 8 * 0.12, 2),
        active_assets=active_assets,
        active_anomalies=active_anomalies,
        pending_recommendations=pending_recs,
        energy_savings_today_kwh=round(savings_kwh, 2),
        co2_reduction_today_kg=round(co2_reduction, 2),
        avg_efficiency=0.82,
        peak_demand_kw=round(total_rated_power * 0.9, 2),
    )


@router.get("/esg", response_model=ESGMetrics)
def get_esg_metrics(db: Session = Depends(get_db)):
    """Get ESG and ISO 50001 compliance metrics."""
    total_power = db.query(func.sum(Asset.rated_power_kw)).scalar() or 0.0
    total_energy = total_power * 24 * 30  # Monthly estimate
    co2_reduction = (
        db.query(func.sum(Recommendation.estimated_co2_reduction_kg))
        .filter(Recommendation.status == RecommendationStatus.EXECUTED)
        .scalar() or 0.0
    )

    return ESGMetrics(
        total_energy_kwh=round(total_energy, 2),
        renewable_energy_kwh=round(total_energy * 0.25, 2),
        renewable_percentage=25.0,
        co2_emissions_kg=round(total_energy * 0.4, 2),  # Grid emission factor
        co2_reduction_kg=round(co2_reduction, 2),
        energy_intensity=round(total_energy / max(1, total_power), 2),
        iso50001_compliance_score=78.5,
        year_over_year_improvement=12.3,
    )

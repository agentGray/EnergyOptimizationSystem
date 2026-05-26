"""Energy baseline model for tracking normal consumption patterns."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.core.database import Base


class EnergyBaseline(Base):
    """
    Energy consumption baseline for an asset.
    
    Used to compare current usage against expected patterns
    to identify waste and optimization opportunities.
    """

    __tablename__ = "energy_baselines"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    period_type = Column(String(50), nullable=False)  # hourly, daily, weekly, monthly
    day_of_week = Column(Integer, nullable=True)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer, nullable=True)  # 0-23
    month = Column(Integer, nullable=True)  # 1-12
    avg_power_kw = Column(Float, nullable=False)
    min_power_kw = Column(Float)
    max_power_kw = Column(Float)
    std_deviation = Column(Float)
    sample_count = Column(Integer, default=0)
    energy_kwh = Column(Float)
    cost_per_kwh = Column(Float, default=0.12)
    notes = Column(Text)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<EnergyBaseline(asset_id={self.asset_id}, "
            f"period='{self.period_type}', avg_power={self.avg_power_kw}kW)>"
        )

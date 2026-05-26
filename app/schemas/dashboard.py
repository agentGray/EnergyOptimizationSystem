"""Pydantic schemas for Dashboard API responses."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class EnergyUsagePoint(BaseModel):
    timestamp: datetime
    power_kw: float
    energy_kwh: float
    cost_usd: float


class DashboardOverview(BaseModel):
    total_power_kw: float
    total_energy_today_kwh: float
    total_cost_today_usd: float
    active_assets: int
    active_anomalies: int
    pending_recommendations: int
    energy_savings_today_kwh: float
    co2_reduction_today_kg: float
    avg_efficiency: float
    peak_demand_kw: float


class AssetEnergyData(BaseModel):
    asset_id: int
    asset_name: str
    asset_type: str
    current_power_kw: float
    energy_today_kwh: float
    efficiency: float
    health_score: float
    status: str


class ZoneEnergyData(BaseModel):
    zone: str
    total_power_kw: float
    asset_count: int
    anomaly_count: int


class ESGMetrics(BaseModel):
    total_energy_kwh: float
    renewable_energy_kwh: float
    renewable_percentage: float
    co2_emissions_kg: float
    co2_reduction_kg: float
    energy_intensity: float  # kWh per unit of production
    iso50001_compliance_score: float
    year_over_year_improvement: float


class LoadProfile(BaseModel):
    hour: int
    avg_power_kw: float
    peak_power_kw: float
    base_load_kw: float
    optimized_power_kw: float

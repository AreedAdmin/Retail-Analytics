"""
KPI (Key Performance Indicator) definitions and calculations for the dashboard.

These KPIs form the high-level metrics displayed in Module 1 (Overview)
and underpin all analytical modules.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class KPI:
    """Single KPI definition with calculation logic."""
    name: str  # display name (e.g., "Total Revenue", "Avg Price")
    value: float  # current value
    unit: str  # e.g., "$", "%", "units", "SKUs"
    change_pct: Optional[float] = None  # period-over-period change (%)
    description: str = ""  # tooltip description


class KPIRegistry:
    """
    Centralized registry of all KPIs used across the dashboard.
    
    This ensures consistent metric definitions and single point of truth
    for how KPIs are calculated.
    """
    
    # Module 1: Overview KPIs
    TOTAL_REVENUE = "total_revenue"
    TOTAL_DEMAND_UNITS = "total_demand_units"
    NUM_SKUS = "num_skus"
    NUM_PERIODS = "num_periods"
    AVG_PRICE = "avg_price"
    NUM_PROMOTIONS = "num_promotions"
    
    # Module 3: Promotion Effectiveness KPIs
    TOTAL_PROMOTION_LIFT = "total_promotion_lift"
    AVG_LIFT_PCT = "avg_lift_pct"
    HIGH_RESPONDER_SKUS = "high_responder_skus"  # count of SKUs with lift > threshold
    
    # Module 4: Price Elasticity KPIs
    AVG_ELASTICITY = "avg_elasticity"
    NUM_ELASTIC_SKUS = "num_elastic_skus"  # elasticity < -1
    NUM_INELASTIC_SKUS = "num_inelastic_skus"  # elasticity > -1
    
    # Module 5: Scenario Testing KPIs
    SCENARIO_REVENUE_IMPACT = "scenario_revenue_impact"
    SCENARIO_DEMAND_IMPACT = "scenario_demand_impact"
    
    # Module 6: Demand Forecasting KPIs
    AVG_FORECAST_ERROR = "avg_forecast_error"  # MAPE or MAE
    FORECAST_UNCERTAINTY = "forecast_uncertainty"  # avg confidence interval width
    
    @staticmethod
    def get_display_name(kpi_id: str) -> str:
        """Convert KPI ID to human-readable display name."""
        mapping = {
            KPIRegistry.TOTAL_REVENUE: "Total Revenue",
            KPIRegistry.TOTAL_DEMAND_UNITS: "Total Demand (Units)",
            KPIRegistry.NUM_SKUS: "Number of SKUs",
            KPIRegistry.NUM_PERIODS: "Analysis Periods",
            KPIRegistry.AVG_PRICE: "Average Price",
            KPIRegistry.NUM_PROMOTIONS: "Promotions Run",
            KPIRegistry.TOTAL_PROMOTION_LIFT: "Total Promotion Lift",
            KPIRegistry.AVG_LIFT_PCT: "Average Lift %",
            KPIRegistry.HIGH_RESPONDER_SKUS: "High-Response SKUs",
            KPIRegistry.AVG_ELASTICITY: "Average Elasticity",
            KPIRegistry.NUM_ELASTIC_SKUS: "Elastic SKUs",
            KPIRegistry.NUM_INELASTIC_SKUS: "Inelastic SKUs",
            KPIRegistry.AVG_FORECAST_ERROR: "Avg Forecast Error",
            KPIRegistry.FORECAST_UNCERTAINTY: "Forecast Uncertainty",
        }
        return mapping.get(kpi_id, kpi_id)
    
    @staticmethod
    def get_unit(kpi_id: str) -> str:
        """Get the unit for a given KPI."""
        mapping = {
            KPIRegistry.TOTAL_REVENUE: "$",
            KPIRegistry.TOTAL_DEMAND_UNITS: "units",
            KPIRegistry.NUM_SKUS: "SKUs",
            KPIRegistry.NUM_PERIODS: "periods",
            KPIRegistry.AVG_PRICE: "$",
            KPIRegistry.NUM_PROMOTIONS: "promos",
            KPIRegistry.TOTAL_PROMOTION_LIFT: "units",
            KPIRegistry.AVG_LIFT_PCT: "%",
            KPIRegistry.HIGH_RESPONDER_SKUS: "SKUs",
            KPIRegistry.AVG_ELASTICITY: "elasticity",
            KPIRegistry.NUM_ELASTIC_SKUS: "SKUs",
            KPIRegistry.NUM_INELASTIC_SKUS: "SKUs",
            KPIRegistry.AVG_FORECAST_ERROR: "%",
            KPIRegistry.FORECAST_UNCERTAINTY: "%",
        }
        return mapping.get(kpi_id, "")


# KPI Thresholds (used for color-coding and alerts)
class KPIThresholds:
    """Define thresholds for KPI health indicators."""
    
    # Promotion lift: SKU is "high responder" if lift > this %
    HIGH_PROMOTION_RESPONSE_THRESHOLD = 10.0  # 10% lift
    
    # Elasticity: SKU is "elastic" if |elasticity| > 1
    ELASTICITY_ELASTICITY_THRESHOLD = 1.0
    
    # Forecast error acceptable range
    FORECAST_ERROR_GOOD = 10.0  # MAPE < 10% is good
    FORECAST_ERROR_ACCEPTABLE = 20.0  # MAPE < 20% is acceptable
    
    # Price change scenarios to test by default
    DEFAULT_PRICE_SCENARIOS = [-30, -20, -10, -5, 5, 10, 20, 30]  # percentage changes

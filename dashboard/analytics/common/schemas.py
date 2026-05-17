"""
Shared data schemas and integration contracts for analytics modules.

These schemas enforce the contracts defined in docs/CLAUDE.md and ensure
cross-team compatibility between ML, Analytics, and AI layers.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ForecastOutput:
    """
    Forecast output contract (Layer 4: ML → Layer 2: Orchestration).
    
    All forecasting models must produce outputs in this format.
    Used by Module 6 (Demand Forecasting) and Module 5 (Scenario Simulator).
    """
    sku_id: str
    period: str  # week or period identifier
    y_true: Optional[float]  # actual demand (if known)
    y_pred: float  # predicted demand
    y_lower: float  # lower confidence bound (e.g., 80th percentile)
    y_upper: float  # upper confidence bound (e.g., 95th percentile)
    model_name: str  # e.g., "gradient_boosting", "lstm"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku_id": self.sku_id,
            "period": self.period,
            "y_true": self.y_true,
            "y_pred": self.y_pred,
            "y_lower": self.y_lower,
            "y_upper": self.y_upper,
            "model_name": self.model_name,
        }


@dataclass
class PromotionOutput:
    """
    Promotion effectiveness output contract (Layer 3: Analytics → Layer 2: Orchestration).
    
    Output from SCAN*PRO analysis or equivalent promotion lift model.
    Used by Module 3 (Promotion Effectiveness) and Module 7 (Promotion Lift Model).
    """
    sku_id: str
    period: str
    promotion_flag: bool  # was promotion active in this period
    incremental_sales: float  # additional sales attributed to promotion
    lift_pct: float  # lift percentage (incremental_sales / baseline_sales * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku_id": self.sku_id,
            "period": self.period,
            "promotion_flag": self.promotion_flag,
            "incremental_sales": self.incremental_sales,
            "lift_pct": self.lift_pct,
        }


@dataclass
class ElasticityOutput:
    """
    Price elasticity output contract (Layer 3: Analytics → Layer 2: Orchestration).
    
    Elasticity coefficient: % change in demand / % change in price.
    Used by Module 4 (Price Elasticity) and Module 5 (Scenario Simulator).
    """
    sku_id: str
    elasticity_value: float  # e.g., -1.2 (elastic), -0.8 (inelastic)
    confidence_low: float  # lower bound of elasticity estimate
    confidence_high: float  # upper bound of elasticity estimate
    model_type: str  # e.g., "log_log_regression"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku_id": self.sku_id,
            "elasticity_value": self.elasticity_value,
            "confidence_low": self.confidence_low,
            "confidence_high": self.confidence_high,
            "model_type": self.model_type,
        }


@dataclass
class ScenarioOutput:
    """
    Scenario simulator output contract (Layer 3: Analytics → Layer 2: Orchestration).
    
    Projects impact of price changes on demand and revenue.
    Used by Module 5 (Scenario Simulator).
    """
    sku_id: str
    scenario_name: str  # e.g., "price_increase_10_pct"
    price_change_pct: float  # e.g., +10.0, -5.0
    demand_change_pct: float  # projected demand change from elasticity
    revenue_change_pct: float  # projected revenue change
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku_id": self.sku_id,
            "scenario_name": self.scenario_name,
            "price_change_pct": self.price_change_pct,
            "demand_change_pct": self.demand_change_pct,
            "revenue_change_pct": self.revenue_change_pct,
        }


@dataclass
class AIContextPayload:
    """
    AI context payload contract (Layer 2: Orchestration → Layer 5: AI Intelligence).
    
    Structured context sent to LLM before generating summaries or Q&A responses.
    Prevents hallucination by grounding all outputs in explicit metrics.
    Used by Module 8 (Chat Interface), click-to-summarise, multi-select summaries.
    """
    module_name: str  # e.g., "promotion_effectiveness", "demand_forecasting"
    chart_id: str  # unique identifier for the chart
    metrics: Dict[str, Any]  # key metrics from the chart (numbers, percentages, etc.)
    key_findings: List[str]  # bullet-point findings to be narrated
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "chart_id": self.chart_id,
            "metrics": self.metrics,
            "key_findings": self.key_findings,
        }
    
    def to_json_string(self) -> str:
        """Serialize to JSON string for LLM context."""
        import json
        return json.dumps(self.to_dict(), indent=2)


# Type aliases for clarity
SKUMetrics = Dict[str, Any]  # SKU-level metrics across modules
ChartData = Dict[str, Any]  # Data structure for a single chart
ModuleOutput = Dict[str, Any]  # Output from a single module

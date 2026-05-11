from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetBundle:
    brand: dict[str, Any]
    company: dict[str, Any]
    products: dict[str, Any]
    reviews: list[dict[str, Any]]
    traffic: dict[str, Any]


@dataclass
class FeatureBundle:
    brand_name: str
    created_years: float
    social_channel_count: int
    contact_channel_count: int
    feature_count: int
    shipping_carrier_count: int
    sales_channel_count: int
    estimated_visits: int
    estimated_sales_yearly: float
    semrush_visits_latest_month: int
    monthly_visits_latest: int
    branded_search_volume: int
    traffic_direct_share: float
    traffic_search_share: float
    traffic_social_share: float
    traffic_top_country_share: float
    top_country_code: str
    review_count: int
    review_avg_stars: float
    review_positive_ratio: float
    review_negative_ratio: float
    sentiment_keywords_top: list[tuple[str, int]]
    complaint_rate_price: float
    complaint_rate_sweet: float
    complaint_rate_artificial: float
    product_count: int
    variant_count: int
    beverage_like_count: int
    merch_count: int
    price_min: float
    price_max: float
    price_avg: float
    recent_product_signal: int
    funding_rounds: int
    investor_count: int
    timeline_event_count: int
    funding_prediction_score: float | None
    acquisition_prediction_score: float | None
    data_quality_notes: list[str] = field(default_factory=list)


@dataclass
class DimensionScore:
    name: str
    score: float | None
    confidence: float
    weight: float
    status: str
    rationale: str
    inputs: dict[str, Any]


@dataclass
class ScoreCard:
    brand_name: str
    total_score: float
    supported_weight: float
    dimensions: list[DimensionScore]
    skipped_dimensions: list[DimensionScore]
    llm_summary: str

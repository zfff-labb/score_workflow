from __future__ import annotations

from .models import DimensionScore, FeatureBundle
from .utils import clamp


def _skip(name: str, weight: float, rationale: str) -> DimensionScore:
    return DimensionScore(
        name=name,
        score=None,
        confidence=0.2,
        weight=weight,
        status="skipped",
        rationale=rationale,
        inputs={},
    )


def score_brand_maturity(features: FeatureBundle) -> DimensionScore:
    years_score = clamp(features.created_years / 10 * 100)
    visit_score = clamp(features.estimated_visits / 2_000_000 * 100)
    coverage_score = clamp(
        features.social_channel_count / 6 * 35
        + features.feature_count / 15 * 35
        + features.contact_channel_count / 10 * 30
    )
    score = round(years_score * 0.35 + visit_score * 0.4 + coverage_score * 0.25, 2)
    confidence = 0.88
    rationale = (
        f"品牌已运营约 {features.created_years} 年，站点估算访问量 {features.estimated_visits}，"
        f"社媒和站点功能覆盖较完整。"
    )
    return DimensionScore(
        name="品牌成熟度",
        score=score,
        confidence=confidence,
        weight=0.22,
        status="supported",
        rationale=rationale,
        inputs={
            "created_years": features.created_years,
            "estimated_visits": features.estimated_visits,
            "social_channel_count": features.social_channel_count,
            "feature_count": features.feature_count,
            "contact_channel_count": features.contact_channel_count,
        },
    )


def score_product_quality(features: FeatureBundle) -> DimensionScore:
    rating_score = clamp(features.review_avg_stars / 5 * 100)
    positive_score = clamp(features.review_positive_ratio * 100)
    complaint_penalty = clamp((features.complaint_rate_sweet * 0.45 + features.complaint_rate_artificial * 0.55) * 100)
    score = round(rating_score * 0.55 + positive_score * 0.3 + (100 - complaint_penalty) * 0.15, 2)
    confidence = 0.81 if features.review_count >= 30 else 0.65
    rationale = (
        f"评论均分 {features.review_avg_stars}，高分评论占比 {features.review_positive_ratio:.1%}，"
        f"但存在甜度和人工甜味相关抱怨。"
    )
    return DimensionScore(
        name="产品质量",
        score=score,
        confidence=confidence,
        weight=0.22,
        status="supported",
        rationale=rationale,
        inputs={
            "review_avg_stars": features.review_avg_stars,
            "review_positive_ratio": features.review_positive_ratio,
            "complaint_rate_sweet": features.complaint_rate_sweet,
            "complaint_rate_artificial": features.complaint_rate_artificial,
        },
    )


def score_demand_fit(features: FeatureBundle) -> DimensionScore:
    traffic_score = clamp(features.monthly_visits_latest / 500_000 * 100)
    search_score = clamp(features.branded_search_volume / 100_000 * 100)
    conversion_proxy = clamp(features.estimated_sales_yearly / 8_000_000_000 * 100)
    score = round(traffic_score * 0.35 + search_score * 0.25 + conversion_proxy * 0.4, 2)
    confidence = 0.76
    rationale = (
        f"最近月访问量 {features.monthly_visits_latest}，品牌搜索量 {features.branded_search_volume}，"
        f"品牌站销售估算与流量规模均显示较强需求匹配。"
    )
    return DimensionScore(
        name="市场需求匹配度",
        score=score,
        confidence=confidence,
        weight=0.2,
        status="supported",
        rationale=rationale,
        inputs={
            "monthly_visits_latest": features.monthly_visits_latest,
            "branded_search_volume": features.branded_search_volume,
            "estimated_sales_yearly": features.estimated_sales_yearly,
        },
    )


def score_innovation(features: FeatureBundle) -> DimensionScore:
    freshness_score = clamp(features.recent_product_signal / 8 * 100)
    funding_score = clamp(features.funding_rounds / 8 * 100)
    momentum_score = clamp((features.funding_prediction_score or 0.5) * 100)
    score = round(freshness_score * 0.35 + funding_score * 0.3 + momentum_score * 0.35, 2)
    confidence = 0.63
    rationale = (
        f"公司存在新品与增长信号，融资轮次 {features.funding_rounds}，"
        f"但产品快照受周边商品干扰，创新分的样本纯度一般。"
    )
    return DimensionScore(
        name="创新力",
        score=score,
        confidence=confidence,
        weight=0.13,
        status="supported",
        rationale=rationale,
        inputs={
            "recent_product_signal": features.recent_product_signal,
            "funding_rounds": features.funding_rounds,
            "funding_prediction_score": features.funding_prediction_score,
        },
    )


def score_operational_resilience(features: FeatureBundle) -> DimensionScore:
    channel_score = clamp(features.shipping_carrier_count / 4 * 35 + features.sales_channel_count / 3 * 25 + features.contact_channel_count / 10 * 40)
    concentration_penalty = clamp(features.traffic_top_country_share * 35)
    score = round(channel_score * 0.75 + (100 - concentration_penalty) * 0.25, 2)
    confidence = 0.68
    rationale = (
        f"具备 {features.shipping_carrier_count} 个物流承运商、{features.sales_channel_count} 个外部销售渠道和多种联络方式，"
        f"但流量高度集中在 {features.top_country_code}。"
    )
    return DimensionScore(
        name="运营韧性",
        score=score,
        confidence=confidence,
        weight=0.13,
        status="supported",
        rationale=rationale,
        inputs={
            "shipping_carrier_count": features.shipping_carrier_count,
            "sales_channel_count": features.sales_channel_count,
            "contact_channel_count": features.contact_channel_count,
            "traffic_top_country_share": features.traffic_top_country_share,
        },
    )


def score_value_for_money(features: FeatureBundle) -> DimensionScore:
    review_value_score = clamp(features.review_avg_stars / 5 * 100)
    price_sentiment_score = clamp((1 - features.complaint_rate_price) * 100)
    price_level_score = 70.0 if 1.0 <= features.price_avg <= 20.0 else 50.0
    if features.merch_count > features.beverage_like_count:
        price_level_score -= 10.0
    score = round(review_value_score * 0.45 + price_sentiment_score * 0.35 + price_level_score * 0.2, 2)
    confidence = 0.57
    rationale = (
        f"用户总体评分较高，但价格相关抱怨占比 {features.complaint_rate_price:.1%}，"
        f"且商品样本受到大量周边商品影响，性价比维度置信度偏低。"
    )
    return DimensionScore(
        name="性价比",
        score=score,
        confidence=confidence,
        weight=0.1,
        status="supported",
        rationale=rationale,
        inputs={
            "review_avg_stars": features.review_avg_stars,
            "complaint_rate_price": features.complaint_rate_price,
            "price_avg": features.price_avg,
            "merch_count": features.merch_count,
            "beverage_like_count": features.beverage_like_count,
        },
    )


def score_skipped_dimensions() -> list[DimensionScore]:
    return [
        _skip("市场趋势契合度", 0.0, "当前样本缺少可直接验证的外部趋势词库与类目级趋势序列。"),
        _skip("可持续发展", 0.0, "缺少第三方认证、ESG 报告或包装材料等可核验数据。"),
        _skip("供应链可靠性", 0.0, "缺少库存、缺货、履约异常与延迟投诉等直接运营数据。"),
    ]


def score_dimensions(features: FeatureBundle) -> tuple[list[DimensionScore], list[DimensionScore]]:
    supported = [
        score_brand_maturity(features),
        score_product_quality(features),
        score_demand_fit(features),
        score_innovation(features),
        score_operational_resilience(features),
        score_value_for_money(features),
    ]
    skipped = score_skipped_dimensions()
    return supported, skipped


def aggregate_score(dimensions: list[DimensionScore]) -> tuple[float, float]:
    weighted_sum = sum((dimension.score or 0.0) * dimension.weight for dimension in dimensions)
    total_weight = sum(dimension.weight for dimension in dimensions if dimension.score is not None)
    if total_weight == 0:
        return 0.0, 0.0
    return round(weighted_sum / total_weight, 2), round(total_weight, 2)

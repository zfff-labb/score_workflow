from __future__ import annotations

import re
from collections import Counter

from .models import DatasetBundle, FeatureBundle
from .utils import iso_to_datetime, safe_float, safe_int, utc_now, years_between


BEVERAGE_TERMS = (
    "cola",
    "ale",
    "apple",
    "temple",
    "soda",
    "drink",
    "cream",
    "lime",
    "grape",
    "orange",
)
MERCH_TERMS = (
    "jacket",
    "sweatsuit",
    "plushie",
    "ornament",
    "beanie",
    "stein",
    "socks",
    "sweater",
    "puzzle",
    "blanket",
    "slippers",
    "glass",
    "keychain",
    "hoodie",
    "dog sweater",
)
STOP_WORDS = {
    "this",
    "that",
    "have",
    "with",
    "from",
    "just",
    "really",
    "they",
    "their",
    "olipop",
    "flavor",
    "flavors",
    "soda",
    "sodas",
    "drink",
    "drinks",
    "would",
    "about",
    "there",
    "because",
    "these",
}


def _normalize_tags(raw_tags) -> list[str]:
    if not raw_tags:
        return []
    if isinstance(raw_tags, str):
        return [item.strip() for item in raw_tags.split(",") if item.strip()]
    if isinstance(raw_tags, list):
        return [str(item).strip() for item in raw_tags if str(item).strip()]
    return []


def _review_keyword_stats(reviews: list[dict]) -> tuple[list[tuple[str, int]], float, float, float]:
    words = Counter()
    price_mentions = 0
    sweet_mentions = 0
    artificial_mentions = 0
    total = max(len(reviews), 1)

    for review in reviews:
        text = f"{review.get('bodyPositive', '')} {review.get('bodyNegative', '')}".lower()
        price_mentions += int(any(term in text for term in ("price", "expensive", "cost", "pricey")))
        sweet_mentions += int(any(term in text for term in ("sweet", "sugary", "sugar")))
        artificial_mentions += int(any(term in text for term in ("artificial", "fake", "aftertaste", "aspartame", "stevia")))
        cleaned = re.sub(r"[^a-z\s]", " ", text)
        for word in cleaned.split():
            if len(word) >= 4 and word not in STOP_WORDS:
                words[word] += 1

    return (
        words.most_common(15),
        round(price_mentions / total, 4),
        round(sweet_mentions / total, 4),
        round(artificial_mentions / total, 4),
    )


def _classify_products(products: list[dict]) -> tuple[int, int]:
    beverage_like_count = 0
    merch_count = 0
    for product in products:
        title = (product.get("title") or "").lower()
        product_type = (product.get("product_type") or "").lower()
        is_merch = "merch" in product_type or "holiday merchandise" in product_type or any(
            term in title for term in MERCH_TERMS
        )
        is_beverage = any(term in title for term in BEVERAGE_TERMS) and not is_merch
        if is_merch:
            merch_count += 1
        elif is_beverage:
            beverage_like_count += 1
    return beverage_like_count, merch_count


def extract_features(bundle: DatasetBundle) -> FeatureBundle:
    brand = bundle.brand["domain"]
    company_cards = bundle.company["cards"]
    products = bundle.products.get("products", [])
    reviews = bundle.reviews
    traffic = bundle.traffic

    created_at = iso_to_datetime(brand.get("created_at"))
    now = utc_now()

    review_stars = [safe_float(review.get("stars")) for review in reviews if review.get("stars") is not None]
    positive_count = sum(1 for star in review_stars if star >= 4)
    negative_count = sum(1 for star in review_stars if star <= 2)
    keyword_stats, complaint_rate_price, complaint_rate_sweet, complaint_rate_artificial = _review_keyword_stats(reviews)

    variant_prices = []
    recent_product_signal = 0
    for product in products:
        title = (product.get("title") or "").lower()
        product_type = (product.get("product_type") or "").lower()
        is_merch = "merch" in product_type or "holiday merchandise" in product_type or any(
            term in title for term in MERCH_TERMS
        )
        is_beverage = any(term in title for term in BEVERAGE_TERMS) and not is_merch
        published_at = iso_to_datetime(product.get("published_at"))
        if is_beverage and published_at and (now - published_at).days <= 365:
            recent_product_signal += 1
        for variant in product.get("variants", []) or []:
            if variant.get("price") is not None:
                variant_prices.append(safe_float(variant.get("price")))

    beverage_like_count, merch_count = _classify_products(products)

    top_keywords = traffic.get("TopKeywords", [])
    branded_search_volume = sum(safe_int(item.get("Volume")) for item in top_keywords[:5])
    top_country = (traffic.get("TopCountryShares") or [{}])[0]
    traffic_sources = traffic.get("TrafficSources", {})

    company_products = company_cards.get("product", [])
    company_timeline = company_cards.get("overview_timeline", {})
    funding_prediction = (company_cards.get("funding_prediction") or [{}])[0]
    acquisition_prediction = (company_cards.get("acquisition_prediction") or [{}])[0]

    quality_notes = []
    if merch_count > beverage_like_count:
        quality_notes.append("products-info 以周边商品为主，核心饮料 SKU 代表性有限")
    if len(reviews) < 100:
        quality_notes.append("评论样本量较小，适合轻量口碑判断，不宜过度外推")
    if safe_float(top_country.get("Value")) > 0.7:
        quality_notes.append("流量高度集中于单一国家，国际化信号有限")

    return FeatureBundle(
        brand_name=brand.get("merchant_name") or brand.get("theme", {}).get("name", "Unknown"),
        created_years=years_between(created_at, now),
        social_channel_count=sum(1 for item in brand.get("contact_info", []) if item.get("type") in {"twitter", "facebook", "instagram", "pinterest", "linkedin", "tiktok"}),
        contact_channel_count=len({item.get("type") for item in brand.get("contact_info", []) if item.get("type")}),
        feature_count=len(brand.get("features", [])),
        shipping_carrier_count=len(brand.get("shipping_carriers", [])),
        sales_channel_count=len(brand.get("sales_channels", [])),
        estimated_visits=safe_int(brand.get("estimated_visits")),
        estimated_sales_yearly=safe_float(brand.get("estimated_sales_yearly")),
        semrush_visits_latest_month=safe_int(company_cards.get("semrush_rank_headline", {}).get("semrush_visits_latest_month")),
        monthly_visits_latest=safe_int(traffic.get("Engagments", {}).get("Visits")),
        branded_search_volume=branded_search_volume,
        traffic_direct_share=safe_float(traffic_sources.get("Direct")),
        traffic_search_share=safe_float(traffic_sources.get("Search")),
        traffic_social_share=safe_float(traffic_sources.get("Social")),
        traffic_top_country_share=safe_float(top_country.get("Value")),
        top_country_code=str(top_country.get("CountryCode", "")),
        review_count=len(reviews),
        review_avg_stars=round(sum(review_stars) / max(len(review_stars), 1), 2),
        review_positive_ratio=round(positive_count / max(len(review_stars), 1), 4),
        review_negative_ratio=round(negative_count / max(len(review_stars), 1), 4),
        sentiment_keywords_top=keyword_stats,
        complaint_rate_price=complaint_rate_price,
        complaint_rate_sweet=complaint_rate_sweet,
        complaint_rate_artificial=complaint_rate_artificial,
        product_count=len(products),
        variant_count=sum(len(product.get("variants", []) or []) for product in products),
        beverage_like_count=beverage_like_count,
        merch_count=merch_count,
        price_min=min(variant_prices) if variant_prices else 0.0,
        price_max=max(variant_prices) if variant_prices else 0.0,
        price_avg=round(sum(variant_prices) / max(len(variant_prices), 1), 2),
        recent_product_signal=recent_product_signal + int(bool(company_products)),
        funding_rounds=safe_int(company_cards.get("funding_rounds_summary", {}).get("num_funding_rounds")),
        investor_count=safe_int(company_cards.get("investors_summary", {}).get("num_investors")),
        timeline_event_count=safe_int(company_timeline.get("count")),
        funding_prediction_score=safe_float(funding_prediction.get("probability_score")) if funding_prediction else None,
        acquisition_prediction_score=safe_float(acquisition_prediction.get("probability_score")) if acquisition_prediction else None,
        data_quality_notes=quality_notes,
    )

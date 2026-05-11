import unittest

from src.score_workflow.metrics import aggregate_score, score_dimensions
from src.score_workflow.models import FeatureBundle


def build_features() -> FeatureBundle:
    return FeatureBundle(
        brand_name="OLIPOP",
        created_years=7.0,
        social_channel_count=6,
        contact_channel_count=8,
        feature_count=13,
        shipping_carrier_count=3,
        sales_channel_count=1,
        estimated_visits=1_600_000,
        estimated_sales_yearly=7_656_001_008.0,
        semrush_visits_latest_month=336_793,
        monthly_visits_latest=402_363,
        branded_search_volume=91_460,
        traffic_direct_share=0.49,
        traffic_search_share=0.39,
        traffic_social_share=0.03,
        traffic_top_country_share=0.71,
        top_country_code="US",
        review_count=50,
        review_avg_stars=4.18,
        review_positive_ratio=0.8,
        review_negative_ratio=0.1,
        sentiment_keywords_top=[("taste", 20)],
        complaint_rate_price=0.18,
        complaint_rate_sweet=0.24,
        complaint_rate_artificial=0.16,
        product_count=30,
        variant_count=190,
        beverage_like_count=3,
        merch_count=25,
        price_min=0.22,
        price_max=60.0,
        price_avg=14.88,
        recent_product_signal=4,
        funding_rounds=7,
        investor_count=46,
        timeline_event_count=120,
        funding_prediction_score=0.92,
        acquisition_prediction_score=0.34,
        data_quality_notes=["products-info 以周边商品为主"],
    )


class MetricsTestCase(unittest.TestCase):
    def test_dimension_count_and_total_score(self):
        supported, skipped = score_dimensions(build_features())
        total_score, total_weight = aggregate_score(supported)
        self.assertEqual(len(supported), 6)
        self.assertEqual(len(skipped), 3)
        self.assertGreater(total_score, 0)
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_dimension_statuses(self):
        supported, skipped = score_dimensions(build_features())
        self.assertTrue(all(item.status == "supported" for item in supported))
        self.assertTrue(all(item.status == "skipped" for item in skipped))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from .data_loader import load_datasets
from .feature_extraction import extract_features
from .llm import generate_summary
from .metrics import aggregate_score, score_dimensions
from .models import ScoreCard
from .reporting import write_outputs


def run_workflow(data_dir: str, output_dir: str) -> ScoreCard:
    bundle = load_datasets(data_dir)
    features = extract_features(bundle)
    supported, skipped = score_dimensions(features)
    total_score, supported_weight = aggregate_score(supported)
    summary = generate_summary(features, supported, total_score)
    scorecard = ScoreCard(
        brand_name=features.brand_name,
        total_score=total_score,
        supported_weight=supported_weight,
        dimensions=supported,
        skipped_dimensions=skipped,
        llm_summary=summary,
    )
    write_outputs(output_dir, scorecard, features)
    return scorecard

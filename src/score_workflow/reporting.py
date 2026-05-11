from __future__ import annotations

import json
from pathlib import Path

from .models import DimensionScore, FeatureBundle, ScoreCard


def _chart_bar(value: float) -> str:
    return "█" * max(1, int(round(value / 5)))


def render_markdown(scorecard: ScoreCard, features: FeatureBundle) -> str:
    lines = [
        f"# {scorecard.brand_name} 品牌评分报告",
        "",
        "## 综合结论",
        "",
        f"- 综合得分：`{scorecard.total_score}`",
        f"- 已纳入计算权重：`{scorecard.supported_weight}`",
        f"- 评论样本：`{features.review_count}`",
        f"- 商品样本：`{features.product_count}`",
        f"- 主要流量国家：`{features.top_country_code}`",
        "",
        "## 各维度得分",
        "",
        "| 维度 | 得分 | 置信度 | 权重 | 状态 | 说明 |",
        "|---|---:|---:|---:|---|---|",
    ]

    for dimension in scorecard.dimensions + scorecard.skipped_dimensions:
        score_value = "-" if dimension.score is None else f"{dimension.score:.2f}"
        lines.append(
            f"| {dimension.name} | {score_value} | {dimension.confidence:.2f} | {dimension.weight:.2f} | {dimension.status} | {dimension.rationale} |"
        )

    lines.extend(
        [
            "",
            "## 中文综合诊断",
            "",
            scorecard.llm_summary,
            "",
            "## 简易可视化",
            "",
        ]
    )

    for dimension in scorecard.dimensions:
        lines.append(f"- {dimension.name}: `{dimension.score:.2f}` {_chart_bar(dimension.score or 0)}")

    lines.extend(
        [
            "",
            "## 数据质量说明",
            "",
        ]
    )
    for note in features.data_quality_notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"


def render_svg(scorecard: ScoreCard) -> str:
    width = 820
    height = 380
    bar_left = 180
    bar_width = 520
    bar_height = 24
    gap = 18
    top = 40
    colors = ["#4F46E5", "#059669", "#D97706", "#DC2626", "#0284C7", "#7C3AED"]

    rows = []
    for index, dimension in enumerate(scorecard.dimensions):
        y = top + index * (bar_height + gap)
        value = dimension.score or 0.0
        filled = bar_width * (value / 100.0)
        color = colors[index % len(colors)]
        rows.append(
            f'<text x="24" y="{y + 17}" font-size="14" fill="#111827">{dimension.name}</text>'
            f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="{bar_height}" fill="#E5E7EB" rx="4" />'
            f'<rect x="{bar_left}" y="{y}" width="{filled:.2f}" height="{bar_height}" fill="{color}" rx="4" />'
            f'<text x="{bar_left + bar_width + 16}" y="{y + 17}" font-size="13" fill="#111827">{value:.2f}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="white"/>'
        f'<text x="24" y="24" font-size="18" font-weight="bold" fill="#111827">{scorecard.brand_name} 品牌评分图</text>'
        + "".join(rows)
        + "</svg>"
    )


def write_outputs(output_dir: str | Path, scorecard: ScoreCard, features: FeatureBundle) -> None:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    summary = {
        "brand_name": scorecard.brand_name,
        "total_score": scorecard.total_score,
        "supported_weight": scorecard.supported_weight,
        "llm_summary": scorecard.llm_summary,
        "dimensions": [
            {
                "name": dimension.name,
                "score": dimension.score,
                "confidence": dimension.confidence,
                "weight": dimension.weight,
                "status": dimension.status,
                "rationale": dimension.rationale,
                "inputs": dimension.inputs,
            }
            for dimension in scorecard.dimensions + scorecard.skipped_dimensions
        ],
        "data_quality_notes": features.data_quality_notes,
    }

    (root / "score_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "report.md").write_text(render_markdown(scorecard, features), encoding="utf-8")
    (root / "score_chart.svg").write_text(render_svg(scorecard), encoding="utf-8")

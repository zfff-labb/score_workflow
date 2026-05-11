from __future__ import annotations

import json
import os
from urllib import error, request

from .models import DimensionScore, FeatureBundle


def _fallback_summary(features: FeatureBundle, dimensions: list[DimensionScore], total_score: float) -> str:
    strongest = max(dimensions, key=lambda item: item.score or 0.0)
    weakest = min(dimensions, key=lambda item: item.score or 0.0)
    return (
        f"{features.brand_name} 的综合得分为 {total_score} 分，整体呈现出较成熟的品牌经营状态。"
        f"品牌成熟度、产品质量和市场需求匹配度表现较强，说明其在品牌认知、用户反馈和站点需求层面具备优势。"
        f"其中 {strongest.name} 是当前最突出的优势维度。"
        f"相对薄弱的环节是 {weakest.name}，主要受到样本结构偏向周边商品、价格敏感反馈和部分维度数据不足的影响。"
        f"建议后续补充更细粒度销售、供应链和 ESG 数据，以提升评分稳定性与可解释性。"
    )


def generate_summary(features: FeatureBundle, dimensions: list[DimensionScore], total_score: float) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        return _fallback_summary(features, dimensions, total_score)

    prompt = {
        "brand_name": features.brand_name,
        "total_score": total_score,
        "dimensions": [
            {
                "name": dimension.name,
                "score": dimension.score,
                "confidence": dimension.confidence,
                "rationale": dimension.rationale,
            }
            for dimension in dimensions
        ],
    }
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名零售品牌分析师，请用中文生成 100-200 字的综合诊断，要求客观、凝练、可执行。",
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                },
            ],
            "temperature": 0.3,
        }
    ).encode("utf-8")
    req = request.Request(
        url=f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
    except (error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return _fallback_summary(features, dimensions, total_score)

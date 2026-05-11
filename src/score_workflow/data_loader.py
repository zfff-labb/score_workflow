from __future__ import annotations

import json
from pathlib import Path

from .models import DatasetBundle


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_datasets(data_dir: str | Path) -> DatasetBundle:
    root = Path(data_dir)
    return DatasetBundle(
        brand=_read_json(root / "brand-info.json"),
        company=_read_json(root / "company-info.json"),
        products=_read_json(root / "products-info.json"),
        reviews=_read_json(root / "review-info.json"),
        traffic=_read_json(root / "traffic-info.json"),
    )

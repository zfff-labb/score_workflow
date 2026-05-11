from __future__ import annotations

from datetime import datetime, timezone


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def iso_to_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def years_between(start: datetime | None, end: datetime | None) -> float:
    if not start or not end:
        return 0.0
    if start.tzinfo is None and end.tzinfo is not None:
        end = end.astimezone(timezone.utc).replace(tzinfo=None)
    elif start.tzinfo is not None and end.tzinfo is None:
        start = start.astimezone(timezone.utc).replace(tzinfo=None)
    delta_days = (end - start).days
    return round(delta_days / 365.25, 2)


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

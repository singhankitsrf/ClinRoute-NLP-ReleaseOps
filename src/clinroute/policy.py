from __future__ import annotations


def review_required(
    route_confidence: float,
    urgency_confidence: float,
    route_min: float = 0.70,
    urgency_min: float = 0.70,
) -> bool:
    return route_confidence < route_min or urgency_confidence < urgency_min

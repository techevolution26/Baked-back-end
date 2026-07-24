"""
Order pricing.

Deliberately simple for now: base template price plus a flat per-sticker
surcharge. This is a placeholder heuristic, not a rules engine -- swap
in per-bakery pricing rules (or per-asset pricing once the sticker
catalog has real prices) once that's needed.
"""
from decimal import Decimal
from typing import Any

STICKER_SURCHARGE = Decimal("200")  # KSh, flat fee per sticker layer


def calculate_blueprint_price(base_price: Decimal, layers: list[dict[str, Any]]) -> Decimal:
    sticker_count = sum(1 for layer in layers if layer.get("type") == "sticker")
    return base_price + (STICKER_SURCHARGE * sticker_count)

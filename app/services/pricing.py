"""
Order pricing.

price = (category's per-kg rate * total kg across all tiers)
        + design fee (the bakery owner's base_price for this template)
        + a flat surcharge per sticker layer
"""
from decimal import Decimal
from typing import Any

CATEGORY_PRICE_PER_KG: dict[str, Decimal] = {
    "red_velvet": Decimal("2000"),
    "vanilla": Decimal("1400"),
    "black_forest": Decimal("2000"),
    "fruit_cake": Decimal("1600"),
    "white_forest": Decimal("2000"),
    "chocolate_cake": Decimal("2000"),
    # PLACEHOLDER -- price wasn't provided, confirm and correct this.
    "strawberry": Decimal("1800"),
}
DEFAULT_CATEGORY = "vanilla"
STICKER_SURCHARGE = Decimal("200")


def total_kg(tiers: list[dict[str, Any]]) -> Decimal:
    return sum((Decimal(str(t.get("kg", 1))) for t in tiers), Decimal("0"))


def calculate_blueprint_price(
    design_price: Decimal,
    category: str,
    tiers: list[dict[str, Any]],
    layers: list[dict[str, Any]],
) -> Decimal:
    category_rate = CATEGORY_PRICE_PER_KG.get(category, CATEGORY_PRICE_PER_KG[DEFAULT_CATEGORY])
    kg = total_kg(tiers)
    sticker_count = sum(1 for layer in layers if layer.get("type") == "sticker")
    return (category_rate * kg) + design_price + (STICKER_SURCHARGE * sticker_count)
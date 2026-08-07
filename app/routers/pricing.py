from fastapi import APIRouter

from ..schemas.pricing import PricingCategoryOut, PricingConfigOut
from ..services.pricing import CATEGORY_PRICE_PER_KG, STICKER_SURCHARGE

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/config", response_model=PricingConfigOut)
async def get_pricing_config():
    return PricingConfigOut(
        categories=[
            PricingCategoryOut(id=key, label=key.replace("_", " ").title(), price_per_kg=float(value))
            for key, value in CATEGORY_PRICE_PER_KG.items()
        ],
        sticker_surcharge=float(STICKER_SURCHARGE),
    )
from pydantic import BaseModel


class PricingCategoryOut(BaseModel):
    id: str
    label: str
    price_per_kg: float


class PricingConfigOut(BaseModel):
    categories: list[PricingCategoryOut]
    sticker_surcharge: float
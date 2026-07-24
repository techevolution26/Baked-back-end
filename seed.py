"""
Quick local-dev seed script -- creates a demo owner account, a bakery
with a platform subdomain, and one design template, so you can exercise
domain resolution and the storefront without building bakery-signup
flows yet.

Usage: python seed.py
"""
import asyncio

from app.core.security import hash_password
from app.core.database import async_session
from app.models import Bakery, DesignTemplate, User, UserRole


async def main():
    async with async_session() as session:
        owner = User(
            username="sweetfig_owner",
            password_hash=hash_password("password123"),
            role=UserRole.bakery_owner,
        )
        session.add(owner)
        await session.flush()

        bakery = Bakery(
            owner_user_id=owner.id,
            name="Sweet Fig Bakery",
            location="Nairobi, Kenya",
            verified=True,
            subdomain="sweetfig",
        )
        session.add(bakery)
        await session.flush()

        owner.bakery_id = bakery.id

        template = DesignTemplate(
            bakery_id=bakery.id,
            name="Classic Two-Tier",
            base_shape="tiered",
            base_price=3500,
            cover_image_url="https://placehold.co/600x600?text=Cake",
            tags=["birthday", "classic"],
            customizable_fields={"tiers": 2},
        )
        session.add(template)

        await session.commit()
        print(f"Seeded '{bakery.name}' at subdomain '{bakery.subdomain}'")
        print("Owner login: username=sweetfig_owner password=password123")
        print(
            "Set DEV_TENANT_HOST=sweetfig.cakeplatform.test in the frontend's "
            ".env.local to browse this storefront locally."
        )


if __name__ == "__main__":
    asyncio.run(main())

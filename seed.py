"""
Quick local-dev seed script -- creates a demo owner account and a bakery
with a platform subdomain so you can exercise domain resolution and the 
storefront without building bakery-signup flows yet.

Safe to run multiple times (Idempotent).
Usage: python seed.py
"""
import asyncio
from sqlalchemy import select

from app.core.security import hash_password
from app.core.database import async_session
from app.models import Bakery, User, UserRole


async def main():
    async with async_session() as session:
        # 1. Seed or Fetch Owner Account
        user_stmt = select(User).where(User.username == "Gracious_owner")
        user_result = await session.execute(user_stmt)
        owner = user_result.scalar_one_or_none()

        if not owner:
            owner = User(
                username="Gracious_owner",
                password_hash=hash_password("password123"),
                role=UserRole.bakery_owner,
            )
            session.add(owner)
            await session.flush()  # Populates owner.id
            print(" Created demo owner account.")
        else:
            print("Demo owner account already exists. Skipping insertion.")

        # 2. Seed or Fetch Bakery
        bakery_stmt = select(Bakery).where(Bakery.subdomain == "gracious")
        bakery_result = await session.execute(bakery_stmt)
        bakery = bakery_result.scalar_one_or_none()

        if not bakery:
            bakery = Bakery(
                owner_user_id=owner.id,
                name="Gracious Bakery",
                location="KIlifi, Kenya",
                verified=True,
                subdomain="gracious",
                rating=5.00,
            )
            session.add(bakery)
            await session.flush()  # Populates bakery.id
            print(f" Created bakery '{bakery.name}' on subdomain '{bakery.subdomain}'.")
        else:
            # Sync owner id if it somehow changed or mismatched
            bakery.owner_user_id = owner.id
            print(f" Created bakery '{bakery.name}' on subdomain '{bakery.subdomain}'.")

        # Ensure the structural bidirectional relation link matches
        if owner.bakery_id != bakery.id:
            owner.bakery_id = bakery.id

        # Commit everything to the database safely
        await session.commit()
        
        print("\n Seeding operations complete!")
        print("Owner login: username=Gracious_owner password=@password123")
        print(
            "Set DEV_TENANT_HOST=gracious.cakeplatform.test in the frontend's "
            ".env.local to browse this storefront locally."
        )


if __name__ == "__main__":
    asyncio.run(main())

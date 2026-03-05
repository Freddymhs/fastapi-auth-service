"""Seed script — creates initial development data.

Usage:
    python seed.py
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session_factory, engine
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

SEED_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin1234",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
    },
    {
        "email": "user@example.com",
        "password": "user1234",
        "full_name": "Usuario Demo",
        "role": UserRole.USER,
    },
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session, session.begin():
        for user_data in SEED_USERS:
            stmt = select(User).where(User.email == user_data["email"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("User '%s' already exists, skipping", user_data["email"])
                continue

            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
            )
            session.add(user)
            logger.info("Created user '%s' (%s)", user_data["email"], user_data["role"])

    logger.info("Seed completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())

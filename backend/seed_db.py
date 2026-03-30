import asyncio
import os
import sys

# Setup path so it can run from backend directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import async_session_factory
from app.models.db_models import User
from app.services.auth_service import AuthService
from sqlalchemy import select

async def seed():
    print("Checking database for users...")
    async with async_session_factory() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            print("No users found. Seeding test users...")
            doctor = User(
                email="doctor@example.com",
                password_hash=AuthService.get_password_hash("password"),
                role="DOCTOR",
            )
            receptionist = User(
                email="receptionist@example.com",
                password_hash=AuthService.get_password_hash("password"),
                role="RECEPTIONIST",
            )
            session.add_all([doctor, receptionist])
            await session.commit()
            print("Created doctor@example.com (password) and receptionist@example.com (password)")
        else:
            print(f"Users already exist: {[u.email for u in users]}")

if __name__ == "__main__":
    asyncio.run(seed())

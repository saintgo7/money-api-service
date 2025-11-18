#!/usr/bin/env python3
"""Create admin user."""
import asyncio
import sys
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, '.')

from src.core.database import AsyncSessionLocal
from src.models.user import User, PlanType
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin():
    """Create admin user interactively."""
    print("Create Admin User\n")

    email = input("Email: ").strip()
    if not email:
        print("Error: Email is required")
        return

    password = getpass("Password: ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return

    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("Error: Passwords don't match")
        return

    full_name = input("Full name (optional): ").strip()

    # Create user
    async with AsyncSessionLocal() as db:
        try:
            # Check if user exists
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.email == email)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Error: User with email {email} already exists")
                return

            # Create new user
            user = User(
                email=email,
                password_hash=pwd_context.hash(password),
                full_name=full_name or None,
                plan=PlanType.ENTERPRISE,  # Admin gets enterprise plan
                credit_balance=1000.00,  # $1000 credits
                is_active=True,
                is_verified=True
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            print(f"\n✅ Admin user created successfully!")
            print(f"Email: {email}")
            print(f"User ID: {user.id}")
            print(f"Plan: {user.plan.value}")
            print(f"Credits: ${user.credit_balance}")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_admin())

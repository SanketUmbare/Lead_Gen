"""Seed a default admin user for development."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.db.base import Base
from app.db.models import User
from app.db.session import SessionLocal, engine


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "admin@leadgen.ai").first()
    if not existing:
        user = User(
            email="admin@leadgen.ai",
            hashed_password=hash_password("admin12345"),
            full_name="Admin User",
        )
        db.add(user)
        db.commit()
        print("Created admin@leadgen.ai / admin12345")
    else:
        print("Admin user already exists")
    db.close()


if __name__ == "__main__":
    seed()

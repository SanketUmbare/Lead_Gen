"""
Base repository pattern.

WHY: Repositories isolate SQL from business logic. When you swap Postgres for
read replicas or add caching, only the repository changes — not your services.
This is how mature SaaS teams avoid "SQL in every file" spaghetti.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def get_by_id(self, id: UUID) -> ModelT | None:
        return self.db.get(self.model, id)

    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelT) -> ModelT:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()

"""Data-access layer: every DB query in the app goes through a Repository.

Services depend on repositories, never on Session/select directly — that's
what makes the service layer's business logic testable without a database.
"""

from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class Repository(Generic[ModelType]):
    """Generic CRUD data access for a single SQLModel table."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get(self, item_id: int) -> ModelType | None:
        return self.session.get(self.model, item_id)

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(self.session.exec(stmt).all())

    def add(self, item: ModelType) -> ModelType:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, item: ModelType, data: dict) -> ModelType:
        for key, value in data.items():
            setattr(item, key, value)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item: ModelType) -> None:
        self.session.delete(item)
        self.session.commit()

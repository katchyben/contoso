from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories import Repository

ModelType = TypeVar("ModelType", bound=SQLModel)


class CrudService(Generic[ModelType]):
    """Generic create/list/get/update/delete backing the CRUD router factory."""

    def __init__(self, repository: Repository[ModelType]):
        self.repository = repository

    def create(self, data: SQLModel) -> ModelType:
        item = self.repository.model.model_validate(data)
        try:
            return self.repository.add(item)
        except IntegrityError as exc:
            self.repository.session.rollback()
            raise ConflictError(str(exc.orig)) from exc

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        return self.repository.list(offset=offset, limit=limit)

    def get(self, item_id: int) -> ModelType:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError(self.repository.model.__name__)
        return item

    def update(self, item_id: int, data: SQLModel) -> ModelType:
        item = self.get(item_id)
        try:
            return self.repository.update(item, data.model_dump(exclude_unset=True))
        except IntegrityError as exc:
            self.repository.session.rollback()
            raise ConflictError(str(exc.orig)) from exc

    def delete(self, item_id: int) -> None:
        item = self.get(item_id)
        self.repository.delete(item)

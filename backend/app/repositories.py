"""Data-access layer: every DB query in the app goes through a Repository.

Services depend on repositories, never on Session/select directly — that's
what makes the service layer's business logic testable without a database.
"""

from typing import Generic, TypeVar

from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from app.models import Customer, Order, OrderItem, User

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


class UserRepository(Repository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        stmt = select(User).where(func.lower(User.email) == normalized)
        return self.session.exec(stmt).first()


class CustomerRepository(Repository[Customer]):
    def __init__(self, session: Session):
        super().__init__(session, Customer)

    def get_by_email(self, email: str) -> Customer | None:
        normalized = email.strip().lower()
        stmt = select(Customer).where(func.lower(Customer.email) == normalized)
        return self.session.exec(stmt).first()


class OrderRepository(Repository[Order]):
    def __init__(self, session: Session):
        super().__init__(session, Order)

    def list_by_customer(self, customer_id: int) -> list[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id).order_by(Order.placed_at.desc())
        return list(self.session.exec(stmt).all())


class OrderItemRepository(Repository[OrderItem]):
    def __init__(self, session: Session):
        super().__init__(session, OrderItem)

    def list_by_order(self, order_id: int) -> list[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        return list(self.session.exec(stmt).all())

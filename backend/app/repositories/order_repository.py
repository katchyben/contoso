from sqlmodel import Session, select

from app.models import Order
from app.repositories.base import Repository


class OrderRepository(Repository[Order]):
    def __init__(self, session: Session):
        super().__init__(session, Order)

    def list_by_customer(self, customer_id: int) -> list[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id).order_by(Order.placed_at.desc())
        return list(self.session.exec(stmt).all())

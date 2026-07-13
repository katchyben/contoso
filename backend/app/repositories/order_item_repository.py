from sqlmodel import Session, select

from app.models import OrderItem
from app.repositories.base import Repository


class OrderItemRepository(Repository[OrderItem]):
    def __init__(self, session: Session):
        super().__init__(session, OrderItem)

    def list_by_order(self, order_id: int) -> list[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        return list(self.session.exec(stmt).all())

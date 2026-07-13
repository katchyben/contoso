from sqlmodel import Session

from app import models, schemas
from app.core.exceptions import NotFoundError
from app.repositories import OrderItemRepository, OrderRepository


class OrderQueryService:
    def __init__(self, session: Session):
        self.order_repository = OrderRepository(session)
        self.order_item_repository = OrderItemRepository(session)

    def list_my_orders(self, customer: models.Customer) -> list[models.Order]:
        return self.order_repository.list_by_customer(customer.id)

    def get_my_order_detail(self, customer: models.Customer, order_id: int) -> schemas.OrderDetailRead:
        order = self.order_repository.get(order_id)
        if order is None or order.customer_id != customer.id:
            raise NotFoundError("Order")
        items = self.order_item_repository.list_by_order(order.id)
        return schemas.OrderDetailRead(
            **order.model_dump(),
            items=[schemas.OrderItemRead.model_validate(i) for i in items],
        )

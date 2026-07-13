from decimal import Decimal

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.order import Order
from app.models.product import Product


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = (UniqueConstraint("order_id", "product_id", name="uq_order_item_product"),)

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    total_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))

    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")

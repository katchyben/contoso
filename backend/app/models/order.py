from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum as SAEnum, Numeric, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import utcnow
from app.models.customer import Customer
from app.models.enums import OrderStatus


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True, max_length=32)
    customer_id: int = Field(foreign_key="customers.id", index=True)
    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        sa_column=Column(SAEnum(OrderStatus, name="order_status"), nullable=False),
    )
    shipping_address_id: int = Field(foreign_key="addresses.id")
    billing_address_id: int = Field(foreign_key="addresses.id")
    subtotal: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    tax_amount: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(10, 2), nullable=False))
    shipping_amount: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(10, 2), nullable=False))
    total_amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    currency: str = Field(default="USD", max_length=3)
    placed_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    )

    customer: Customer = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    payments: list["Payment"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    shipments: list["Shipment"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum as SAEnum, Numeric, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import utcnow
from app.models.enums import PaymentStatus
from app.models.order import Order


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    currency: str = Field(default="USD", max_length=3)
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        sa_column=Column(SAEnum(PaymentStatus, name="payment_status"), nullable=False),
    )
    provider: str = Field(max_length=50)  # e.g. "stripe", "paypal"
    provider_reference: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    order: Order = Relationship(back_populates="payments")

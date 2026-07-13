from datetime import datetime

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ShipmentStatus
from app.models.order import Order


class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    carrier: str = Field(max_length=100)
    tracking_number: str | None = Field(default=None, max_length=100)
    status: ShipmentStatus = Field(
        default=ShipmentStatus.PENDING,
        sa_column=Column(SAEnum(ShipmentStatus, name="shipment_status"), nullable=False),
    )
    shipped_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)

    order: Order = Relationship(back_populates="shipments")

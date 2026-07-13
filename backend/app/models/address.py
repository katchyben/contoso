from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.customer import Customer
from app.models.enums import AddressType


class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id", index=True)
    type: AddressType = Field(sa_column=Column(SAEnum(AddressType, name="address_type")))
    line1: str = Field(max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(max_length=2)  # ISO 3166-1 alpha-2
    is_default: bool = Field(default=False)

    customer: Customer = Relationship(back_populates="addresses")

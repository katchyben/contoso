from decimal import Decimal

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.models.category import Category


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=64)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    unit_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock_quantity: int = Field(default=0)
    is_active: bool = Field(default=True)
    image_url: str | None = Field(default=None, max_length=500)
    category_id: int | None = Field(default=None, foreign_key="categories.id", index=True)

    category: Category | None = Relationship(back_populates="products")
    order_items: list["OrderItem"] = Relationship(back_populates="product")

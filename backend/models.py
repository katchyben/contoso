import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum as SAEnum, Numeric, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AddressType(str, enum.Enum):
    SHIPPING = "shipping"
    BILLING = "billing"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    FULFILLING = "fulfilling"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    addresses: list["Address"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    orders: list["Order"] = Relationship(back_populates="customer")


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


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    parent_id: int | None = Field(default=None, foreign_key="categories.id")

    parent: "Category" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: list["Category"] = Relationship(back_populates="parent")
    products: list["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=64)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    unit_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock_quantity: int = Field(default=0)
    is_active: bool = Field(default=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id", index=True)

    category: Category | None = Relationship(back_populates="products")
    order_items: list["OrderItem"] = Relationship(back_populates="product")


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
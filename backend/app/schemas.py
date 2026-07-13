from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.models import AddressType, OrderStatus, PaymentStatus, ShipmentStatus, UserRole


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(SQLModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class CustomerCreate(SQLModel):
    email: str
    first_name: str
    last_name: str
    phone: str | None = None


class CustomerUpdate(SQLModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class CustomerRead(SQLModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None
    created_at: datetime


class AddressCreate(SQLModel):
    customer_id: int
    type: AddressType
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str
    is_default: bool = False


class AddressUpdate(SQLModel):
    type: AddressType | None = None
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


class AddressRead(SQLModel):
    id: int
    customer_id: int
    type: AddressType
    line1: str
    line2: str | None
    city: str
    state: str | None
    postal_code: str
    country: str
    is_default: bool


class CategoryCreate(SQLModel):
    name: str
    parent_id: int | None = None


class CategoryUpdate(SQLModel):
    name: str | None = None
    parent_id: int | None = None


class CategoryRead(SQLModel):
    id: int
    name: str
    parent_id: int | None


class ProductCreate(SQLModel):
    sku: str
    name: str
    description: str | None = None
    unit_price: Decimal
    stock_quantity: int = 0
    is_active: bool = True
    image_url: str | None = None
    category_id: int | None = None


class ProductUpdate(SQLModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    unit_price: Decimal | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None
    image_url: str | None = None
    category_id: int | None = None


class ProductRead(SQLModel):
    id: int
    sku: str
    name: str
    description: str | None
    unit_price: Decimal
    stock_quantity: int
    is_active: bool
    image_url: str | None
    category_id: int | None


class OrderCreate(SQLModel):
    order_number: str
    customer_id: int
    shipping_address_id: int
    billing_address_id: int
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    shipping_amount: Decimal = Decimal("0")
    total_amount: Decimal
    currency: str = "USD"


class OrderUpdate(SQLModel):
    order_number: str | None = None
    status: OrderStatus | None = None
    shipping_address_id: int | None = None
    billing_address_id: int | None = None
    subtotal: Decimal | None = None
    tax_amount: Decimal | None = None
    shipping_amount: Decimal | None = None
    total_amount: Decimal | None = None
    currency: str | None = None


class OrderRead(SQLModel):
    id: int
    order_number: str
    customer_id: int
    status: OrderStatus
    shipping_address_id: int
    billing_address_id: int
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    currency: str
    placed_at: datetime
    updated_at: datetime


class OrderItemCreate(SQLModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderItemUpdate(SQLModel):
    quantity: int | None = None
    unit_price: Decimal | None = None
    total_price: Decimal | None = None


class OrderItemRead(SQLModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderDetailRead(OrderRead):
    items: list[OrderItemRead]


class RegisterRequest(SQLModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str | None = None


class CheckoutAddressInput(SQLModel):
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str


class CheckoutLineItem(SQLModel):
    product_id: int
    quantity: int


class CheckoutRequest(SQLModel):
    shipping_address: CheckoutAddressInput
    billing_address: CheckoutAddressInput | None = None
    items: list[CheckoutLineItem]


class PaymentCreate(SQLModel):
    order_id: int
    amount: Decimal
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    provider: str
    provider_reference: str | None = None


class PaymentUpdate(SQLModel):
    amount: Decimal | None = None
    currency: str | None = None
    status: PaymentStatus | None = None
    provider: str | None = None
    provider_reference: str | None = None


class PaymentRead(SQLModel):
    id: int
    order_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: str
    provider_reference: str | None
    created_at: datetime


class ShipmentCreate(SQLModel):
    order_id: int
    carrier: str
    tracking_number: str | None = None
    status: ShipmentStatus = ShipmentStatus.PENDING
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None


class ShipmentUpdate(SQLModel):
    carrier: str | None = None
    tracking_number: str | None = None
    status: ShipmentStatus | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None


class ShipmentRead(SQLModel):
    id: int
    order_id: int
    carrier: str
    tracking_number: str | None
    status: ShipmentStatus
    shipped_at: datetime | None
    delivered_at: datetime | None

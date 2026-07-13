"""Wires the generic CRUD router factory up for every domain model."""

from fastapi import APIRouter

from app import models, schemas
from app.routers.crud import build_crud_router

customers_router = build_crud_router(
    model=models.Customer,
    create_schema=schemas.CustomerCreate,
    update_schema=schemas.CustomerUpdate,
    read_schema=schemas.CustomerRead,
    prefix="/customers",
    tags=["customers"],
)

addresses_router = build_crud_router(
    model=models.Address,
    create_schema=schemas.AddressCreate,
    update_schema=schemas.AddressUpdate,
    read_schema=schemas.AddressRead,
    prefix="/addresses",
    tags=["addresses"],
)

categories_router = build_crud_router(
    model=models.Category,
    create_schema=schemas.CategoryCreate,
    update_schema=schemas.CategoryUpdate,
    read_schema=schemas.CategoryRead,
    prefix="/categories",
    tags=["categories"],
    read_roles=None,
)

products_router = build_crud_router(
    model=models.Product,
    create_schema=schemas.ProductCreate,
    update_schema=schemas.ProductUpdate,
    read_schema=schemas.ProductRead,
    prefix="/products",
    tags=["products"],
    read_roles=None,
)

orders_router = build_crud_router(
    model=models.Order,
    create_schema=schemas.OrderCreate,
    update_schema=schemas.OrderUpdate,
    read_schema=schemas.OrderRead,
    prefix="/orders",
    tags=["orders"],
)

order_items_router = build_crud_router(
    model=models.OrderItem,
    create_schema=schemas.OrderItemCreate,
    update_schema=schemas.OrderItemUpdate,
    read_schema=schemas.OrderItemRead,
    prefix="/order-items",
    tags=["order-items"],
)

payments_router = build_crud_router(
    model=models.Payment,
    create_schema=schemas.PaymentCreate,
    update_schema=schemas.PaymentUpdate,
    read_schema=schemas.PaymentRead,
    prefix="/payments",
    tags=["payments"],
)

shipments_router = build_crud_router(
    model=models.Shipment,
    create_schema=schemas.ShipmentCreate,
    update_schema=schemas.ShipmentUpdate,
    read_schema=schemas.ShipmentRead,
    prefix="/shipments",
    tags=["shipments"],
)

all_routers: list[APIRouter] = [
    customers_router,
    addresses_router,
    categories_router,
    products_router,
    orders_router,
    order_items_router,
    payments_router,
    shipments_router,
]

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from crud import build_crud_router
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    build_crud_router(
        model=models.Customer,
        create_schema=schemas.CustomerCreate,
        update_schema=schemas.CustomerUpdate,
        read_schema=schemas.CustomerRead,
        prefix="/customers",
        tags=["customers"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Address,
        create_schema=schemas.AddressCreate,
        update_schema=schemas.AddressUpdate,
        read_schema=schemas.AddressRead,
        prefix="/addresses",
        tags=["addresses"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Category,
        create_schema=schemas.CategoryCreate,
        update_schema=schemas.CategoryUpdate,
        read_schema=schemas.CategoryRead,
        prefix="/categories",
        tags=["categories"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Product,
        create_schema=schemas.ProductCreate,
        update_schema=schemas.ProductUpdate,
        read_schema=schemas.ProductRead,
        prefix="/products",
        tags=["products"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Order,
        create_schema=schemas.OrderCreate,
        update_schema=schemas.OrderUpdate,
        read_schema=schemas.OrderRead,
        prefix="/orders",
        tags=["orders"],
    )
)
app.include_router(
    build_crud_router(
        model=models.OrderItem,
        create_schema=schemas.OrderItemCreate,
        update_schema=schemas.OrderItemUpdate,
        read_schema=schemas.OrderItemRead,
        prefix="/order-items",
        tags=["order-items"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Payment,
        create_schema=schemas.PaymentCreate,
        update_schema=schemas.PaymentUpdate,
        read_schema=schemas.PaymentRead,
        prefix="/payments",
        tags=["payments"],
    )
)
app.include_router(
    build_crud_router(
        model=models.Shipment,
        create_schema=schemas.ShipmentCreate,
        update_schema=schemas.ShipmentUpdate,
        read_schema=schemas.ShipmentRead,
        prefix="/shipments",
        tags=["shipments"],
    )
)

"""Business logic layer. Services use repositories to touch the DB and raise
exceptions.py errors on failure — no FastAPI/HTTPException imports here.
"""

import secrets
from decimal import ROUND_HALF_UP, Decimal
from typing import Generic, TypeVar

import jwt
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel

from app import models, schemas
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.repositories import (
    CustomerRepository,
    OrderItemRepository,
    OrderRepository,
    Repository,
    UserRepository,
)

ModelType = TypeVar("ModelType", bound=SQLModel)

TAX_RATE = Decimal("0.08")
FLAT_SHIPPING = Decimal("9.99")
FREE_SHIPPING_THRESHOLD = Decimal("150.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CrudService(Generic[ModelType]):
    """Generic create/list/get/update/delete backing the CRUD router factory."""

    def __init__(self, repository: Repository[ModelType]):
        self.repository = repository

    def create(self, data: SQLModel) -> ModelType:
        item = self.repository.model.model_validate(data)
        try:
            return self.repository.add(item)
        except IntegrityError as exc:
            self.repository.session.rollback()
            raise ConflictError(str(exc.orig)) from exc

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        return self.repository.list(offset=offset, limit=limit)

    def get(self, item_id: int) -> ModelType:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError(self.repository.model.__name__)
        return item

    def update(self, item_id: int, data: SQLModel) -> ModelType:
        item = self.get(item_id)
        try:
            return self.repository.update(item, data.model_dump(exclude_unset=True))
        except IntegrityError as exc:
            self.repository.session.rollback()
            raise ConflictError(str(exc.orig)) from exc

    def delete(self, item_id: int) -> None:
        item = self.get(item_id)
        self.repository.delete(item)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, email: str, password: str) -> models.User:
        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        return user

    def issue_token(self, user: models.User) -> str:
        return create_access_token(subject=user.email, role=user.role.value)

    def get_current_user(self, token: str) -> models.User:
        try:
            payload = decode_access_token(token)
            email = payload.get("sub")
            if email is None:
                raise UnauthorizedError()
        except jwt.PyJWTError as exc:
            raise UnauthorizedError() from exc

        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            raise UnauthorizedError()
        return user


class RegistrationService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        user_repository: UserRepository,
        auth_service: AuthService,
    ):
        self.customer_repository = customer_repository
        self.user_repository = user_repository
        self.auth_service = auth_service

    def register(self, payload: schemas.RegisterRequest) -> str:
        normalized_email = payload.email.strip().lower()
        if self.customer_repository.get_by_email(normalized_email) is not None:
            raise ConflictError("An account with that email already exists. Please log in.")

        customer = self.customer_repository.add(
            models.Customer(
                email=normalized_email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone=payload.phone,
            )
        )
        user = self.user_repository.add(
            models.User(
                email=normalized_email,
                hashed_password=hash_password(payload.password),
                full_name=f"{payload.first_name} {payload.last_name}",
                role=models.UserRole.CUSTOMER,
                customer_id=customer.id,
            )
        )
        return self.auth_service.issue_token(user)


class CheckoutService:
    def __init__(self, session: Session):
        self.product_repository = Repository(session, models.Product)
        self.address_repository = Repository(session, models.Address)
        self.order_repository = OrderRepository(session)
        self.order_item_repository = OrderItemRepository(session)
        self.payment_repository = Repository(session, models.Payment)

    def checkout(self, customer: models.Customer, payload: schemas.CheckoutRequest) -> schemas.OrderDetailRead:
        if not payload.items:
            raise ConflictError("Cart is empty")

        products: dict[int, models.Product] = {}
        for line in payload.items:
            if line.quantity <= 0:
                raise ConflictError("Quantity must be positive")
            product = self.product_repository.get(line.product_id)
            if product is None or not product.is_active:
                raise ConflictError(f"Product {line.product_id} is not available")
            if product.stock_quantity < line.quantity:
                raise ConflictError(f'Not enough stock for "{product.name}"')
            products[line.product_id] = product

        shipping = self.address_repository.add(
            models.Address(
                customer_id=customer.id,
                type=models.AddressType.SHIPPING,
                **payload.shipping_address.model_dump(),
            )
        )
        billing_data = payload.billing_address or payload.shipping_address
        billing = self.address_repository.add(
            models.Address(
                customer_id=customer.id,
                type=models.AddressType.BILLING,
                **billing_data.model_dump(),
            )
        )

        subtotal = money(
            sum((products[line.product_id].unit_price * line.quantity for line in payload.items), Decimal("0"))
        )
        shipping_amount = Decimal("0.00") if subtotal >= FREE_SHIPPING_THRESHOLD else FLAT_SHIPPING
        tax_amount = money(subtotal * TAX_RATE)
        total_amount = money(subtotal + shipping_amount + tax_amount)

        order = self.order_repository.add(
            models.Order(
                order_number=f"WEB-{secrets.token_hex(4).upper()}",
                customer_id=customer.id,
                status=models.OrderStatus.PAID,
                shipping_address_id=shipping.id,
                billing_address_id=billing.id,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_amount=shipping_amount,
                total_amount=total_amount,
            )
        )

        items: list[models.OrderItem] = []
        for line in payload.items:
            product = products[line.product_id]
            item = self.order_item_repository.add(
                models.OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=line.quantity,
                    unit_price=product.unit_price,
                    total_price=money(product.unit_price * line.quantity),
                )
            )
            product.stock_quantity -= line.quantity
            self.product_repository.add(product)
            items.append(item)

        self.payment_repository.add(
            models.Payment(
                order_id=order.id,
                amount=total_amount,
                status=models.PaymentStatus.CAPTURED,
                provider="mock",
                provider_reference=f"mock_{order.order_number.lower()}",
            )
        )

        # The order-item and payment commits above expire `order` (SQLAlchemy's
        # default expire_on_commit) — refresh it so model_dump() below doesn't
        # serialize an empty/stale instance.
        self.order_repository.session.refresh(order)

        return schemas.OrderDetailRead(
            **order.model_dump(),
            items=[schemas.OrderItemRead.model_validate(i) for i in items],
        )


class OrderQueryService:
    def __init__(self, session: Session):
        self.order_repository = OrderRepository(session)
        self.order_item_repository = OrderItemRepository(session)

    def list_my_orders(self, customer: models.Customer) -> list[models.Order]:
        return self.order_repository.list_by_customer(customer.id)

    def get_my_order_detail(self, customer: models.Customer, order_id: int) -> schemas.OrderDetailRead:
        order = self.order_repository.get(order_id)
        if order is None or order.customer_id != customer.id:
            raise NotFoundError("Order")
        items = self.order_item_repository.list_by_order(order.id)
        return schemas.OrderDetailRead(
            **order.model_dump(),
            items=[schemas.OrderItemRead.model_validate(i) for i in items],
        )

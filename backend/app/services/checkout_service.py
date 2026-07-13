import secrets
from decimal import ROUND_HALF_UP, Decimal

from sqlmodel import Session

from app import models, schemas
from app.core.exceptions import ConflictError
from app.repositories import OrderItemRepository, OrderRepository, Repository

TAX_RATE = Decimal("0.08")
FLAT_SHIPPING = Decimal("9.99")
FREE_SHIPPING_THRESHOLD = Decimal("150.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


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

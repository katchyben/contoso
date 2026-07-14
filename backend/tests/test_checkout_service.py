from decimal import Decimal

import pytest

from app import models, schemas
from app.core.exceptions import ConflictError
from app.repositories import CustomerRepository, Repository
from app.services.checkout_service import CheckoutService

SHIPPING_ADDRESS = schemas.CheckoutAddressInput(
    line1="1 Main St", city="Springfield", postal_code="00000", country="US"
)


@pytest.fixture()
def customer(session):
    return CustomerRepository(session).add(
        models.Customer(email="shopper@example.com", first_name="Shop", last_name="Per")
    )


@pytest.fixture()
def cheap_product(session):
    return Repository(session, models.Product).add(
        models.Product(sku="CHEAP-1", name="Cheap Widget", unit_price=Decimal("10.00"), stock_quantity=5)
    )


@pytest.fixture()
def expensive_product(session):
    return Repository(session, models.Product).add(
        models.Product(sku="EXP-1", name="Expensive Gadget", unit_price=Decimal("200.00"), stock_quantity=5)
    )


@pytest.fixture()
def inactive_product(session):
    return Repository(session, models.Product).add(
        models.Product(
            sku="INACTIVE-1", name="Discontinued", unit_price=Decimal("10.00"), stock_quantity=5, is_active=False
        )
    )


def test_checkout_happy_path_computes_totals_and_creates_order(session, customer, cheap_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=cheap_product.id, quantity=2)],
    )

    order = service.checkout(customer, request)

    assert order.subtotal == Decimal("20.00")
    assert order.shipping_amount == Decimal("9.99")  # below free-shipping threshold
    assert order.tax_amount == Decimal("1.60")  # 8% of 20.00
    assert order.total_amount == Decimal("31.59")
    assert order.status == models.OrderStatus.PAID
    assert len(order.items) == 1


def test_checkout_waives_shipping_above_free_threshold(session, customer, expensive_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=expensive_product.id, quantity=1)],
    )

    order = service.checkout(customer, request)

    assert order.subtotal == Decimal("200.00")
    assert order.shipping_amount == Decimal("0.00")


def test_checkout_decrements_stock(session, customer, cheap_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=cheap_product.id, quantity=2)],
    )

    service.checkout(customer, request)

    session.refresh(cheap_product)
    assert cheap_product.stock_quantity == 3


def test_checkout_rejects_empty_cart(session, customer):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(shipping_address=SHIPPING_ADDRESS, items=[])

    with pytest.raises(ConflictError):
        service.checkout(customer, request)


def test_checkout_rejects_nonpositive_quantity(session, customer, cheap_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=cheap_product.id, quantity=0)],
    )

    with pytest.raises(ConflictError):
        service.checkout(customer, request)


def test_checkout_rejects_inactive_product(session, customer, inactive_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=inactive_product.id, quantity=1)],
    )

    with pytest.raises(ConflictError):
        service.checkout(customer, request)


def test_checkout_rejects_insufficient_stock(session, customer, cheap_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=cheap_product.id, quantity=999)],
    )

    with pytest.raises(ConflictError):
        service.checkout(customer, request)


def test_checkout_defaults_billing_address_to_shipping_when_omitted(session, customer, cheap_product):
    service = CheckoutService(session)
    request = schemas.CheckoutRequest(
        shipping_address=SHIPPING_ADDRESS,
        items=[schemas.CheckoutLineItem(product_id=cheap_product.id, quantity=1)],
    )

    order = service.checkout(customer, request)

    shipping = Repository(session, models.Address).get(order.shipping_address_id)
    billing = Repository(session, models.Address).get(order.billing_address_id)
    assert billing.line1 == shipping.line1
    assert billing.type == models.AddressType.BILLING

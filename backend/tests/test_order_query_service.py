import pytest

from app import models
from app.core.exceptions import NotFoundError
from app.repositories import CustomerRepository, OrderRepository
from app.services.order_query_service import OrderQueryService


@pytest.fixture()
def customer(session):
    return CustomerRepository(session).add(
        models.Customer(email="c@example.com", first_name="C", last_name="Customer")
    )


@pytest.fixture()
def other_customer(session):
    return CustomerRepository(session).add(
        models.Customer(email="other@example.com", first_name="O", last_name="Other")
    )


@pytest.fixture()
def order(session, customer):
    return OrderRepository(session).add(
        models.Order(
            order_number="ORD-1",
            customer_id=customer.id,
            status=models.OrderStatus.PAID,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=10,
            total_amount=10,
        )
    )


def test_list_my_orders_returns_only_that_customers_orders(session, customer, other_customer, order):
    OrderRepository(session).add(
        models.Order(
            order_number="ORD-OTHER",
            customer_id=other_customer.id,
            status=models.OrderStatus.PENDING,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=5,
            total_amount=5,
        )
    )

    service = OrderQueryService(session)
    orders = service.list_my_orders(customer)

    assert [o.order_number for o in orders] == ["ORD-1"]


def test_get_my_order_detail_returns_items(session, customer, order):
    service = OrderQueryService(session)
    detail = service.get_my_order_detail(customer, order.id)
    assert detail.order_number == "ORD-1"
    assert detail.items == []


def test_get_my_order_detail_raises_not_found_for_missing_order(session, customer):
    service = OrderQueryService(session)
    with pytest.raises(NotFoundError):
        service.get_my_order_detail(customer, 999999)


def test_get_my_order_detail_raises_not_found_for_other_customers_order(session, other_customer, order):
    service = OrderQueryService(session)
    with pytest.raises(NotFoundError):
        service.get_my_order_detail(other_customer, order.id)

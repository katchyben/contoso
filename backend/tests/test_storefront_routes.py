from decimal import Decimal

import pytest

from app import models
from app.repositories import Repository


@pytest.fixture()
def product(session):
    return Repository(session, models.Product).add(
        models.Product(sku="SKU-1", name="Widget", unit_price=Decimal("19.99"), stock_quantity=10)
    )


def checkout_payload(product_id: int, quantity: int = 1) -> dict:
    return {
        "shipping_address": {
            "line1": "1 Main St",
            "city": "Springfield",
            "postal_code": "00000",
            "country": "US",
        },
        "items": [{"product_id": product_id, "quantity": quantity}],
    }


def test_checkout_succeeds_for_authenticated_customer(client, make_customer, issue_token, auth_headers, product):
    _, user, _ = make_customer()
    token = issue_token(user)

    response = client.post(
        "/checkout", json=checkout_payload(product.id, 2), headers=auth_headers(token)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["subtotal"] == "39.98"
    assert len(body["items"]) == 1


def test_checkout_rejects_unauthenticated_request(client, product):
    response = client.post("/checkout", json=checkout_payload(product.id))
    assert response.status_code == 401


def test_checkout_rejects_staff_account(client, make_staff_user, issue_token, auth_headers, product):
    user, _ = make_staff_user()
    token = issue_token(user)

    response = client.post(
        "/checkout", json=checkout_payload(product.id), headers=auth_headers(token)
    )

    assert response.status_code == 403


def test_my_orders_returns_only_own_orders(client, make_customer, issue_token, auth_headers, product):
    _, user_a, _ = make_customer(email="a@example.com")
    _, user_b, _ = make_customer(email="b@example.com")
    token_a = issue_token(user_a)
    token_b = issue_token(user_b)

    client.post("/checkout", json=checkout_payload(product.id), headers=auth_headers(token_a))

    response_a = client.get("/me/orders", headers=auth_headers(token_a))
    response_b = client.get("/me/orders", headers=auth_headers(token_b))

    assert len(response_a.json()) == 1
    assert len(response_b.json()) == 0


def test_my_order_detail_returns_404_for_other_customers_order(
    client, make_customer, issue_token, auth_headers, product
):
    _, user_a, _ = make_customer(email="a@example.com")
    _, user_b, _ = make_customer(email="b@example.com")
    token_a = issue_token(user_a)
    token_b = issue_token(user_b)

    order = client.post(
        "/checkout", json=checkout_payload(product.id), headers=auth_headers(token_a)
    ).json()

    response = client.get(f"/me/orders/{order['id']}", headers=auth_headers(token_b))

    assert response.status_code == 404

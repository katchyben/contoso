from app.models import UserRole


def test_products_list_is_public(client):
    response = client.get("/products")
    assert response.status_code == 200


def test_products_create_requires_staff_or_admin(client):
    response = client.post(
        "/products", json={"sku": "SKU-1", "name": "Widget", "unit_price": "9.99", "stock_quantity": 1}
    )
    assert response.status_code == 401


def test_products_create_succeeds_for_staff(client, make_staff_user, issue_token, auth_headers):
    user, _ = make_staff_user(role=UserRole.STAFF)
    token = issue_token(user)

    response = client.post(
        "/products",
        json={"sku": "SKU-1", "name": "Widget", "unit_price": "9.99", "stock_quantity": 1},
        headers=auth_headers(token),
    )

    assert response.status_code == 201


def test_customers_list_requires_auth(client):
    response = client.get("/customers")
    assert response.status_code == 401


def test_customers_list_rejects_customer_role(client, make_customer, issue_token, auth_headers):
    _, user, _ = make_customer()
    token = issue_token(user)

    response = client.get("/customers", headers=auth_headers(token))

    assert response.status_code == 403


def test_customers_list_allows_staff(client, make_staff_user, issue_token, auth_headers):
    user, _ = make_staff_user(role=UserRole.STAFF)
    token = issue_token(user)

    response = client.get("/customers", headers=auth_headers(token))

    assert response.status_code == 200


def test_get_missing_product_returns_404(client, make_staff_user, issue_token, auth_headers):
    response = client.get("/products/999999")
    assert response.status_code == 404


def test_delete_requires_admin_not_just_staff(client, make_staff_user, issue_token, auth_headers):
    staff_user, _ = make_staff_user(email="staff@example.com", role=UserRole.STAFF)
    staff_token = issue_token(staff_user)

    create_response = client.post(
        "/products",
        json={"sku": "SKU-DEL", "name": "Deletable", "unit_price": "1.00", "stock_quantity": 1},
        headers=auth_headers(staff_token),
    )
    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}", headers=auth_headers(staff_token))

    assert response.status_code == 403


def test_delete_succeeds_for_admin(client, make_staff_user, issue_token, auth_headers):
    admin_user, _ = make_staff_user(email="admin@example.com", role=UserRole.ADMIN)
    admin_token = issue_token(admin_user)

    create_response = client.post(
        "/products",
        json={"sku": "SKU-DEL2", "name": "Deletable", "unit_price": "1.00", "stock_quantity": 1},
        headers=auth_headers(admin_token),
    )
    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}", headers=auth_headers(admin_token))

    assert response.status_code == 204

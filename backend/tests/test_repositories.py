from app.models import Category, Customer, Order, OrderItem, OrderStatus, Product, User, UserRole
from app.repositories import (
    CustomerRepository,
    OrderItemRepository,
    OrderRepository,
    Repository,
    UserRepository,
)
from app.core.security import hash_password


def test_repository_add_get_update_delete(session):
    repo = Repository(session, Category)
    category = repo.add(Category(name="Electronics"))
    assert category.id is not None

    fetched = repo.get(category.id)
    assert fetched.name == "Electronics"

    updated = repo.update(fetched, {"name": "Home Electronics"})
    assert updated.name == "Home Electronics"

    repo.delete(updated)
    assert repo.get(category.id) is None


def test_repository_list_respects_offset_and_limit(session):
    repo = Repository(session, Category)
    for i in range(5):
        repo.add(Category(name=f"Cat {i}"))

    page = repo.list(offset=1, limit=2)
    assert len(page) == 2


def test_customer_repository_get_by_email_is_case_insensitive(session):
    repo = CustomerRepository(session)
    repo.add(Customer(email="Ada@Example.com", first_name="Ada", last_name="Lovelace"))

    assert repo.get_by_email("ada@example.com") is not None
    assert repo.get_by_email("nope@example.com") is None


def test_user_repository_get_by_email_is_case_insensitive(session):
    repo = UserRepository(session)
    repo.add(
        User(
            email="Staff@Example.com",
            hashed_password=hash_password("pw"),
            full_name="Staff Member",
            role=UserRole.STAFF,
        )
    )

    assert repo.get_by_email("staff@example.com") is not None
    assert repo.get_by_email("nope@example.com") is None


def test_order_repository_list_by_customer_orders_by_placed_at_desc(session):
    customer = CustomerRepository(session).add(
        Customer(email="c@example.com", first_name="C", last_name="Customer")
    )
    other_customer = CustomerRepository(session).add(
        Customer(email="other@example.com", first_name="O", last_name="Other")
    )
    order_repo = OrderRepository(session)
    order_repo.add(
        Order(
            order_number="ORD-1",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=10,
            total_amount=10,
        )
    )
    order_repo.add(
        Order(
            order_number="ORD-2",
            customer_id=customer.id,
            status=OrderStatus.PAID,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=20,
            total_amount=20,
        )
    )
    order_repo.add(
        Order(
            order_number="ORD-OTHER",
            customer_id=other_customer.id,
            status=OrderStatus.PENDING,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=5,
            total_amount=5,
        )
    )

    orders = order_repo.list_by_customer(customer.id)
    assert {o.order_number for o in orders} == {"ORD-1", "ORD-2"}


def test_order_item_repository_list_by_order(session):
    customer = CustomerRepository(session).add(
        Customer(email="c@example.com", first_name="C", last_name="Customer")
    )
    product = Repository(session, Product).add(
        Product(sku="SKU-1", name="Widget", unit_price=9.99, stock_quantity=10)
    )
    order = OrderRepository(session).add(
        Order(
            order_number="ORD-1",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=9.99,
            total_amount=9.99,
        )
    )
    item_repo = OrderItemRepository(session)
    item_repo.add(
        OrderItem(order_id=order.id, product_id=product.id, quantity=1, unit_price=9.99, total_price=9.99)
    )

    items = item_repo.list_by_order(order.id)
    assert len(items) == 1
    assert items[0].product_id == product.id

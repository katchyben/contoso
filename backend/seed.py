"""Wipes and repopulates the database with sample data for local development.

Run inside the backend container so it reaches Postgres via the Docker network:
    docker compose exec backend uv run python seed.py
"""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import text
from sqlmodel import Session

from app.core.security import hash_password
from app.database import create_db_and_tables, engine
from app.models import (
    Address,
    AddressType,
    Category,
    Customer,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    Product,
    Shipment,
    ShipmentStatus,
    User,
    UserRole,
)

TAX_RATE = Decimal("0.08")
FLAT_SHIPPING = Decimal("9.99")
FREE_SHIPPING_THRESHOLD = Decimal("150.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def clear_data(session: Session) -> None:
    session.execute(
        text(
            "TRUNCATE TABLE shipments, payments, order_items, orders, "
            "addresses, products, categories, customers, users RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


def seed_users(session: Session) -> None:
    session.add_all(
        [
            User(
                email="admin@contoso.local",
                hashed_password=hash_password("admin123"),
                full_name="Ada Administrator",
                role=UserRole.ADMIN,
            ),
            User(
                email="staff@contoso.local",
                hashed_password=hash_password("staff123"),
                full_name="Sam Staff",
                role=UserRole.STAFF,
            ),
        ]
    )
    session.commit()


def seed_customer_login(session: Session, customer: Customer) -> None:
    session.add(
        User(
            email=customer.email,
            hashed_password=hash_password("customer123"),
            full_name=f"{customer.first_name} {customer.last_name}",
            role=UserRole.CUSTOMER,
            customer_id=customer.id,
        )
    )
    session.commit()


def seed_customers(session: Session) -> list[Customer]:
    customers = [
        Customer(email="ada.lovelace@example.com", first_name="Ada", last_name="Lovelace", phone="555-0101"),
        Customer(email="grace.hopper@example.com", first_name="Grace", last_name="Hopper", phone="555-0102"),
        Customer(email="alan.turing@example.com", first_name="Alan", last_name="Turing", phone="555-0103"),
        Customer(email="margaret.hamilton@example.com", first_name="Margaret", last_name="Hamilton", phone="555-0104"),
        Customer(email="katherine.johnson@example.com", first_name="Katherine", last_name="Johnson", phone="555-0105"),
    ]
    session.add_all(customers)
    session.commit()
    for c in customers:
        session.refresh(c)
    return customers


def seed_addresses(session: Session, customers: list[Customer]) -> dict[str, Address]:
    ada, grace, alan, margaret, katherine = customers

    addresses = {
        "ada_shipping": Address(
            customer_id=ada.id, type=AddressType.SHIPPING, line1="12 Analytical Engine Way",
            city="London", postal_code="EC1A 1BB", country="GB", is_default=True,
        ),
        "ada_billing": Address(
            customer_id=ada.id, type=AddressType.BILLING, line1="12 Analytical Engine Way",
            city="London", postal_code="EC1A 1BB", country="GB", is_default=True,
        ),
        "grace_shipping": Address(
            customer_id=grace.id, type=AddressType.SHIPPING, line1="1 Compiler Court",
            city="Arlington", state="VA", postal_code="22201", country="US", is_default=True,
        ),
        "grace_billing": Address(
            customer_id=grace.id, type=AddressType.BILLING, line1="1 Compiler Court",
            city="Arlington", state="VA", postal_code="22201", country="US", is_default=True,
        ),
        "alan_shipping": Address(
            customer_id=alan.id, type=AddressType.SHIPPING, line1="Bletchley Park Rd",
            city="Milton Keynes", postal_code="MK3 6EB", country="GB", is_default=True,
        ),
        "alan_billing": Address(
            customer_id=alan.id, type=AddressType.BILLING, line1="Bletchley Park Rd",
            city="Milton Keynes", postal_code="MK3 6EB", country="GB", is_default=True,
        ),
        "margaret_shipping": Address(
            customer_id=margaret.id, type=AddressType.SHIPPING, line1="4 Apollo Guidance Ln",
            city="Cambridge", state="MA", postal_code="02139", country="US", is_default=True,
        ),
        "margaret_billing": Address(
            customer_id=margaret.id, type=AddressType.BILLING, line1="4 Apollo Guidance Ln",
            city="Cambridge", state="MA", postal_code="02139", country="US", is_default=True,
        ),
        "katherine_shipping": Address(
            customer_id=katherine.id, type=AddressType.SHIPPING, line1="1 Trajectory Blvd",
            city="Hampton", state="VA", postal_code="23666", country="US", is_default=True,
        ),
        "katherine_billing": Address(
            customer_id=katherine.id, type=AddressType.BILLING, line1="1 Trajectory Blvd",
            city="Hampton", state="VA", postal_code="23666", country="US", is_default=True,
        ),
    }
    session.add_all(addresses.values())
    session.commit()
    for address in addresses.values():
        session.refresh(address)
    return addresses


def seed_categories(session: Session) -> dict[str, Category]:
    electronics = Category(name="Electronics")
    home_kitchen = Category(name="Home & Kitchen")
    session.add_all([electronics, home_kitchen])
    session.commit()
    session.refresh(electronics)
    session.refresh(home_kitchen)

    laptops = Category(name="Laptops", parent_id=electronics.id)
    phones = Category(name="Phones", parent_id=electronics.id)
    accessories = Category(name="Accessories", parent_id=electronics.id)
    cookware = Category(name="Cookware", parent_id=home_kitchen.id)
    bakeware = Category(name="Bakeware", parent_id=home_kitchen.id)
    session.add_all([laptops, phones, accessories, cookware, bakeware])
    session.commit()
    for c in (laptops, phones, accessories, cookware, bakeware):
        session.refresh(c)

    return {
        "electronics": electronics,
        "home_kitchen": home_kitchen,
        "laptops": laptops,
        "phones": phones,
        "accessories": accessories,
        "cookware": cookware,
        "bakeware": bakeware,
    }


def image_for(keyword: str, lock: int) -> str:
    # Real, keyword-matched photos via LoremFlickr (searches tagged Flickr
    # photos). `lock` pins a specific photo so it stays stable across reloads
    # instead of returning a new random match each time.
    return f"https://loremflickr.com/480/360/{keyword}?lock={lock}"


def seed_products(session: Session, categories: dict[str, Category]) -> dict[str, Product]:
    products = {
        "ultrabook": Product(
            sku="LAP-ULT-14", name="UltraBook 14", description="14-inch ultraportable laptop",
            unit_price=Decimal("1299.99"), stock_quantity=25, category_id=categories["laptops"].id,
            image_url=image_for("laptop", 101),
        ),
        "probook": Product(
            sku="LAP-PRO-16", name="ProBook 16", description="16-inch workstation laptop",
            unit_price=Decimal("1599.00"), stock_quantity=15, category_id=categories["laptops"].id,
            image_url=image_for("laptop-computer", 1),
        ),
        "pixel_nova": Product(
            sku="PHN-NOVA", name="Pixel Nova", description="Flagship smartphone",
            unit_price=Decimal("899.00"), stock_quantity=40, category_id=categories["phones"].id,
            image_url=image_for("smartphone", 6),
        ),
        "iris_phone": Product(
            sku="PHN-IRIS-12", name="Iris Phone 12", description="Mid-range smartphone",
            unit_price=Decimal("649.99"), stock_quantity=60, category_id=categories["phones"].id,
            image_url=image_for("touchscreen-phone", 1),
        ),
        "wireless_mouse": Product(
            sku="ACC-MOU-01", name="Wireless Mouse", description="Ergonomic wireless mouse",
            unit_price=Decimal("29.99"), stock_quantity=200, category_id=categories["accessories"].id,
            image_url=image_for("computer-mouse", 105),
        ),
        "usb_hub": Product(
            sku="ACC-HUB-01", name="USB-C Hub", description="7-in-1 USB-C hub",
            unit_price=Decimal("45.50"), stock_quantity=150, category_id=categories["accessories"].id,
            image_url=image_for("usb-cable", 1),
        ),
        "frypan": Product(
            sku="CKW-FRY-10", name='NonStick Frypan 10"', description="10-inch nonstick frypan",
            unit_price=Decimal("34.99"), stock_quantity=80, category_id=categories["cookware"].id,
            image_url=image_for("frying-pan", 107),
        ),
        "pot_set": Product(
            sku="CKW-POT-SET", name="Stainless Steel Pot Set", description="5-piece pot and pan set",
            unit_price=Decimal("129.99"), stock_quantity=30, category_id=categories["cookware"].id,
            image_url=image_for("saucepan", 1),
        ),
        "baking_mat": Product(
            sku="BAK-MAT-01", name="Silicone Baking Mat", description="Non-stick silicone baking mat",
            unit_price=Decimal("19.99"), stock_quantity=100, category_id=categories["bakeware"].id,
            image_url=image_for("baking-mat", 1),
        ),
        "muffin_tin": Product(
            sku="BAK-TIN-12", name="Muffin Tin 12-cup", description="Non-stick 12-cup muffin tin",
            unit_price=Decimal("14.99"), stock_quantity=90, category_id=categories["bakeware"].id,
            image_url=image_for("muffin-pan", 1),
        ),
    }
    session.add_all(products.values())
    session.commit()
    for p in products.values():
        session.refresh(p)
    return products


def create_order(
    session: Session,
    *,
    order_number: str,
    customer: Customer,
    shipping_address: Address,
    billing_address: Address,
    status: OrderStatus,
    line_items: list[tuple[Product, int]],
    payment_status: PaymentStatus,
    payment_provider: str = "stripe",
    shipment_status: ShipmentStatus | None = None,
    carrier: str | None = None,
) -> Order:
    subtotal = money(sum((p.unit_price * qty for p, qty in line_items), Decimal("0")))
    shipping_amount = Decimal("0.00") if subtotal >= FREE_SHIPPING_THRESHOLD else FLAT_SHIPPING
    tax_amount = money(subtotal * TAX_RATE)
    total_amount = money(subtotal + shipping_amount + tax_amount)

    order = Order(
        order_number=order_number,
        customer_id=customer.id,
        status=status,
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    for product, qty in line_items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=product.unit_price,
                total_price=money(product.unit_price * qty),
            )
        )

    session.add(
        Payment(
            order_id=order.id,
            amount=total_amount,
            status=payment_status,
            provider=payment_provider,
            provider_reference=f"pi_{order_number.lower()}",
        )
    )

    if shipment_status is not None:
        session.add(
            Shipment(
                order_id=order.id,
                carrier=carrier or "UPS",
                tracking_number=f"1Z{order_number.replace('-', '')}",
                status=shipment_status,
            )
        )

    session.commit()
    return order


def seed_orders(
    session: Session,
    customers: list[Customer],
    addresses: dict[str, Address],
    products: dict[str, Product],
) -> None:
    ada, grace, alan, margaret, katherine = customers

    create_order(
        session,
        order_number="ORD-1001",
        customer=ada,
        shipping_address=addresses["ada_shipping"],
        billing_address=addresses["ada_billing"],
        status=OrderStatus.DELIVERED,
        line_items=[(products["ultrabook"], 1), (products["wireless_mouse"], 2)],
        payment_status=PaymentStatus.CAPTURED,
        shipment_status=ShipmentStatus.DELIVERED,
    )

    create_order(
        session,
        order_number="ORD-1002",
        customer=ada,
        shipping_address=addresses["ada_shipping"],
        billing_address=addresses["ada_billing"],
        status=OrderStatus.PENDING,
        line_items=[(products["usb_hub"], 1)],
        payment_status=PaymentStatus.PENDING,
        shipment_status=None,
    )

    create_order(
        session,
        order_number="ORD-1003",
        customer=grace,
        shipping_address=addresses["grace_shipping"],
        billing_address=addresses["grace_billing"],
        status=OrderStatus.SHIPPED,
        line_items=[(products["pixel_nova"], 1), (products["baking_mat"], 1)],
        payment_status=PaymentStatus.CAPTURED,
        shipment_status=ShipmentStatus.IN_TRANSIT,
        carrier="FedEx",
    )

    create_order(
        session,
        order_number="ORD-1004",
        customer=alan,
        shipping_address=addresses["alan_shipping"],
        billing_address=addresses["alan_billing"],
        status=OrderStatus.CONFIRMED,
        line_items=[(products["probook"], 1)],
        payment_status=PaymentStatus.AUTHORIZED,
        shipment_status=None,
    )

    create_order(
        session,
        order_number="ORD-1005",
        customer=margaret,
        shipping_address=addresses["margaret_shipping"],
        billing_address=addresses["margaret_billing"],
        status=OrderStatus.CANCELLED,
        line_items=[(products["muffin_tin"], 2)],
        payment_status=PaymentStatus.REFUNDED,
        shipment_status=None,
    )

    create_order(
        session,
        order_number="ORD-1006",
        customer=katherine,
        shipping_address=addresses["katherine_shipping"],
        billing_address=addresses["katherine_billing"],
        status=OrderStatus.PAID,
        line_items=[(products["pot_set"], 1), (products["frypan"], 1)],
        payment_status=PaymentStatus.CAPTURED,
        shipment_status=ShipmentStatus.PENDING,
        carrier="USPS",
    )


def main() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        print("Clearing existing data...")
        clear_data(session)

        print("Seeding users...")
        seed_users(session)

        print("Seeding customers...")
        customers = seed_customers(session)

        print("Seeding customer login (ada.lovelace@example.com / customer123)...")
        seed_customer_login(session, customers[0])

        print("Seeding addresses...")
        addresses = seed_addresses(session, customers)

        print("Seeding categories...")
        categories = seed_categories(session)

        print("Seeding products...")
        products = seed_products(session, categories)

        print("Seeding orders, order items, payments, shipments...")
        seed_orders(session, customers, addresses, products)

    print("Done.")


if __name__ == "__main__":
    main()





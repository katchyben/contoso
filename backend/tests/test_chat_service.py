from decimal import Decimal
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app import models
from app.repositories import CustomerRepository, OrderRepository, Repository
from app.services.chat_service import ChatService


@pytest.fixture()
def customer(session):
    return CustomerRepository(session).add(
        models.Customer(email="c@example.com", first_name="Ada", last_name="Lovelace")
    )


def test_system_message_includes_active_products_and_excludes_inactive(session, customer):
    Repository(session, models.Product).add(
        models.Product(sku="ACT-1", name="Active Widget", unit_price=Decimal("9.99"), stock_quantity=3)
    )
    Repository(session, models.Product).add(
        models.Product(
            sku="INACT-1", name="Retired Gadget", unit_price=Decimal("5.00"), stock_quantity=0, is_active=False
        )
    )

    service = ChatService(session)
    message = service._build_system_message(customer)

    assert isinstance(message, SystemMessage)
    assert "Active Widget" in message.content
    assert "Retired Gadget" not in message.content


def test_system_message_includes_customers_own_orders(session, customer):
    OrderRepository(session).add(
        models.Order(
            order_number="ORD-1",
            customer_id=customer.id,
            status=models.OrderStatus.SHIPPED,
            shipping_address_id=1,
            billing_address_id=1,
            subtotal=10,
            total_amount=10,
        )
    )

    service = ChatService(session)
    message = service._build_system_message(customer)

    assert "ORD-1" in message.content
    assert "shipped" in message.content


def test_system_message_handles_no_products_or_orders(session, customer):
    service = ChatService(session)
    message = service._build_system_message(customer)

    assert "No products currently available." in message.content
    assert "No orders yet." in message.content


def test_reply_sends_history_as_typed_messages_and_returns_llm_content(session, customer):
    service = ChatService(session)
    captured = {}

    def fake_invoke(self, messages):
        captured["messages"] = messages
        return AIMessage(content="Here is my answer.")

    with patch("app.services.chat_service.ChatGoogleGenerativeAI.invoke", new=fake_invoke):
        reply = service.reply(
            customer,
            [
                {"role": "user", "content": "Do you have widgets?"},
                {"role": "assistant", "content": "Yes we do."},
                {"role": "user", "content": "Great, how much?"},
            ],
        )

    assert reply == "Here is my answer."
    messages = captured["messages"]
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert isinstance(messages[2], AIMessage)
    assert isinstance(messages[3], HumanMessage)
    assert messages[-1].content == "Great, how much?"

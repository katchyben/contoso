import os

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlmodel import Session

from app import models
from app.repositories import OrderRepository, Repository

STORE_FAQ = """Store info:
- Shipping: orders ship within 2 business days; standard delivery takes 3-5 business days.
- Returns: unused items can be returned within 30 days of delivery for a full refund.
- Support hours: Monday-Friday, 9am-6pm ET.
- Payment: all major credit cards are accepted at checkout.
"""

SYSTEM_PROMPT_TEMPLATE = """You are the customer support assistant for the Contoso online store.
Answer only using the information below. If the answer isn't in there, say you don't have
that information and suggest the customer contact support. Keep replies short and friendly.

{faq}

Product catalog (name, SKU, price, stock):
{catalog}

{customer_name}'s recent orders:
{orders}
"""


class ChatService:
    """Answers customer chat questions using product/order context grounded via Ollama."""

    def __init__(self, session: Session):
        self.product_repository = Repository(session, models.Product)
        self.order_repository = OrderRepository(session)
        self._llm = ChatOllama(
            model=os.environ.get("OLLAMA_MODEL", "mistral"),
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    def _build_system_message(self, customer: models.Customer) -> SystemMessage:
        products = [p for p in self.product_repository.list(limit=200) if p.is_active]
        catalog = "\n".join(f"- {p.name} (SKU {p.sku}): ${p.unit_price}, {p.stock_quantity} in stock" for p in products)

        orders = self.order_repository.list_by_customer(customer.id)[:20]
        order_lines = "\n".join(
            f"- Order {o.order_number}: status={o.status.value}, total=${o.total_amount}, "
            f"placed {o.placed_at.date().isoformat()}"
            for o in orders
        )

        return SystemMessage(
            content=SYSTEM_PROMPT_TEMPLATE.format(
                faq=STORE_FAQ,
                catalog=catalog or "No products currently available.",
                customer_name=customer.first_name,
                orders=order_lines or "No orders yet.",
            )
        )

    def reply(self, customer: models.Customer, history: list[dict]) -> str:
        messages: list[BaseMessage] = [self._build_system_message(customer)]
        for turn in history:
            message_cls = HumanMessage if turn["role"] == "user" else AIMessage
            messages.append(message_cls(content=turn["content"]))
        response = self._llm.invoke(messages)
        return str(response.content)
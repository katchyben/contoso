from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Customer
from app.repositories.base import Repository


class CustomerRepository(Repository[Customer]):
    def __init__(self, session: Session):
        super().__init__(session, Customer)

    def get_by_email(self, email: str) -> Customer | None:
        normalized = email.strip().lower()
        stmt = select(Customer).where(func.lower(Customer.email) == normalized)
        return self.session.exec(stmt).first()

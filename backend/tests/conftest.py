import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("GOOGLE_API_KEY", "test-google-api-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.security import hash_password
from app.database import get_session
from app.main import app
from app.models import Customer, User, UserRole
from app.repositories import UserRepository
from app.services.auth_service import AuthService


@pytest.fixture()
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture()
def session(engine):
    with Session(engine) as db_session:
        yield db_session


@pytest.fixture()
def client(engine):
    def override_get_session():
        with Session(engine) as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def make_customer(session):
    """Creates a Customer + its linked CUSTOMER-role User. Returns (customer, user, password)."""

    def _make(email="ada@example.com", password="password123", first_name="Ada", last_name="Lovelace"):
        customer = Customer(email=email, first_name=first_name, last_name=last_name)
        session.add(customer)
        session.commit()
        session.refresh(customer)

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=f"{first_name} {last_name}",
            role=UserRole.CUSTOMER,
            customer_id=customer.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return customer, user, password

    return _make


@pytest.fixture()
def make_staff_user(session):
    """Creates a non-customer User (staff/admin). Returns (user, password)."""

    def _make(email="staff@example.com", password="password123", role=UserRole.STAFF):
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Staff Member",
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user, password

    return _make


@pytest.fixture()
def issue_token(session):
    def _issue(user: User) -> str:
        return AuthService(UserRepository(session)).issue_token(user)

    return _issue


@pytest.fixture()
def auth_headers():
    def _headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    return _headers

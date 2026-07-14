import pytest

from app import schemas
from app.core.exceptions import ConflictError
from app.core.security import decode_access_token
from app.repositories import CustomerRepository, UserRepository
from app.services.auth_service import AuthService
from app.services.registration_service import RegistrationService


@pytest.fixture()
def service(session):
    return RegistrationService(
        CustomerRepository(session),
        UserRepository(session),
        AuthService(UserRepository(session)),
    )


def test_register_creates_customer_and_user_and_returns_valid_token(service):
    payload = schemas.RegisterRequest(
        email="New.Customer@Example.com",
        password="password123",
        first_name="New",
        last_name="Customer",
    )
    token = service.register(payload)

    payload_claims = decode_access_token(token)
    assert payload_claims["sub"] == "new.customer@example.com"
    assert payload_claims["role"] == "customer"


def test_register_normalizes_email_case(service, session):
    payload = schemas.RegisterRequest(
        email="Mixed.Case@Example.com", password="password123", first_name="Mixed", last_name="Case"
    )
    service.register(payload)

    customer = CustomerRepository(session).get_by_email("mixed.case@example.com")
    assert customer is not None
    assert customer.email == "mixed.case@example.com"


def test_register_rejects_duplicate_email(service):
    payload = schemas.RegisterRequest(
        email="dupe@example.com", password="password123", first_name="Dupe", last_name="One"
    )
    service.register(payload)

    with pytest.raises(ConflictError):
        service.register(payload)

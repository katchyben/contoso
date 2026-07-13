from app import models, schemas
from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.repositories import CustomerRepository, UserRepository
from app.services.auth_service import AuthService


class RegistrationService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        user_repository: UserRepository,
        auth_service: AuthService,
    ):
        self.customer_repository = customer_repository
        self.user_repository = user_repository
        self.auth_service = auth_service

    def register(self, payload: schemas.RegisterRequest) -> str:
        normalized_email = payload.email.strip().lower()
        if self.customer_repository.get_by_email(normalized_email) is not None:
            raise ConflictError("An account with that email already exists. Please log in.")

        customer = self.customer_repository.add(
            models.Customer(
                email=normalized_email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone=payload.phone,
            )
        )
        user = self.user_repository.add(
            models.User(
                email=normalized_email,
                hashed_password=hash_password(payload.password),
                full_name=f"{payload.first_name} {payload.last_name}",
                role=models.UserRole.CUSTOMER,
                customer_id=customer.id,
            )
        )
        return self.auth_service.issue_token(user)

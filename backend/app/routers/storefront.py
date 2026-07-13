from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import models, schemas
from app.core.exceptions import ConflictError, NotFoundError
from app.database import get_session
from app.dependencies import get_current_user
from app.repositories import CustomerRepository, UserRepository
from app.services import AuthService, CheckoutService, OrderQueryService, RegistrationService

router = APIRouter(tags=["storefront"])


def get_current_customer(
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> models.Customer:
    if user.role != models.UserRole.CUSTOMER or user.customer_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer account required")
    customer = CustomerRepository(session).get(user.customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


def get_registration_service(session: Session = Depends(get_session)) -> RegistrationService:
    return RegistrationService(
        CustomerRepository(session),
        UserRepository(session),
        AuthService(UserRepository(session)),
    )


def get_checkout_service(session: Session = Depends(get_session)) -> CheckoutService:
    return CheckoutService(session)


def get_order_query_service(session: Session = Depends(get_session)) -> OrderQueryService:
    return OrderQueryService(session)


@router.post("/auth/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.RegisterRequest, service: RegistrationService = Depends(get_registration_service)):
    try:
        token = service.register(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return schemas.Token(access_token=token)


@router.post("/checkout", response_model=schemas.OrderDetailRead, status_code=201)
def checkout(
    payload: schemas.CheckoutRequest,
    service: CheckoutService = Depends(get_checkout_service),
    customer: models.Customer = Depends(get_current_customer),
):
    try:
        return service.checkout(customer, payload)
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/me/orders", response_model=list[schemas.OrderRead])
def my_orders(
    service: OrderQueryService = Depends(get_order_query_service),
    customer: models.Customer = Depends(get_current_customer),
):
    return service.list_my_orders(customer)


@router.get("/me/orders/{order_id}", response_model=schemas.OrderDetailRead)
def my_order_detail(
    order_id: int,
    service: OrderQueryService = Depends(get_order_query_service),
    customer: models.Customer = Depends(get_current_customer),
):
    try:
        return service.get_my_order_detail(customer, order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

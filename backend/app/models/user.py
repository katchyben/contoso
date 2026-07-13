from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SAEnum, func
from sqlmodel import Field, SQLModel

from app.models.base import utcnow
from app.models.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    full_name: str = Field(max_length=200)
    role: UserRole = Field(
        default=UserRole.STAFF,
        sa_column=Column(SAEnum(UserRole, name="user_role"), nullable=False),
    )
    # Set only for role=CUSTOMER: links this login to its storefront Customer record.
    customer_id: int | None = Field(default=None, foreign_key="customers.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

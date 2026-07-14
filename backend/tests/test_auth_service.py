import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models import User, UserRole
from app.repositories import UserRepository
from app.services.auth_service import AuthService
from app.core.security import hash_password


@pytest.fixture()
def user_repo(session):
    return UserRepository(session)


@pytest.fixture()
def active_user(session, user_repo):
    return user_repo.add(
        User(
            email="staff@example.com",
            hashed_password=hash_password("correct-password"),
            full_name="Staff Member",
            role=UserRole.STAFF,
        )
    )


def test_authenticate_succeeds_with_correct_credentials(user_repo, active_user):
    service = AuthService(user_repo)
    user = service.authenticate("staff@example.com", "correct-password")
    assert user.id == active_user.id


def test_authenticate_rejects_wrong_password(user_repo, active_user):
    service = AuthService(user_repo)
    with pytest.raises(UnauthorizedError):
        service.authenticate("staff@example.com", "wrong-password")


def test_authenticate_rejects_unknown_email(user_repo):
    service = AuthService(user_repo)
    with pytest.raises(UnauthorizedError):
        service.authenticate("nobody@example.com", "whatever")


def test_authenticate_rejects_inactive_user(session, user_repo):
    user_repo.add(
        User(
            email="inactive@example.com",
            hashed_password=hash_password("pw"),
            full_name="Inactive",
            role=UserRole.STAFF,
            is_active=False,
        )
    )
    service = AuthService(user_repo)
    with pytest.raises(UnauthorizedError):
        service.authenticate("inactive@example.com", "pw")


def test_issue_token_embeds_email_and_role(user_repo, active_user):
    service = AuthService(user_repo)
    token = service.issue_token(active_user)
    payload = decode_access_token(token)
    assert payload["sub"] == "staff@example.com"
    assert payload["role"] == "staff"


def test_get_current_user_returns_user_for_valid_token(user_repo, active_user):
    service = AuthService(user_repo)
    token = service.issue_token(active_user)
    user = service.get_current_user(token)
    assert user.id == active_user.id


def test_get_current_user_rejects_garbage_token(user_repo):
    service = AuthService(user_repo)
    with pytest.raises(UnauthorizedError):
        service.get_current_user("not-a-real-token")


def test_get_current_user_rejects_deactivated_user_after_token_issued(user_repo, active_user, session):
    service = AuthService(user_repo)
    token = service.issue_token(active_user)

    active_user.is_active = False
    session.add(active_user)
    session.commit()

    with pytest.raises(UnauthorizedError):
        service.get_current_user(token)

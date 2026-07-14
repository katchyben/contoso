import pytest
import jwt

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plaintext():
    hashed = hash_password("s3cret!")
    assert hashed != "s3cret!"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("s3cret!")
    assert verify_password("s3cret!", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("s3cret!")
    assert verify_password("wrong-password", hashed) is False


def test_access_token_round_trips_subject_and_role():
    token = create_access_token(subject="ada@example.com", role="customer")
    payload = decode_access_token(token)
    assert payload["sub"] == "ada@example.com"
    assert payload["role"] == "customer"


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(subject="ada@example.com", role="customer")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered)

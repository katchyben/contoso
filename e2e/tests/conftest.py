import os
import subprocess
import time
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

BACKEND_PORT = int(os.environ.get("E2E_BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.environ.get("E2E_FRONTEND_PORT", "5173"))
DB_PORT = int(os.environ.get("E2E_DB_PORT", "5433"))

BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"
DATABASE_URL = f"postgresql+psycopg://postgres:postgres@localhost:{DB_PORT}/contoso"

# Seeded by backend/seed.py — see that file for the full fixture set.
CUSTOMER_EMAIL = "ada.lovelace@example.com"
CUSTOMER_PASSWORD = "customer123"
ADMIN_EMAIL = "admin@contoso.local"
ADMIN_PASSWORD = "admin123"


def _wait_until_up(url: str, timeout: float = 60) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            requests.get(url, timeout=2)
            return
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url} to come up") from last_error


@pytest.fixture(scope="session")
def docker_stack():
    """Ensures the project's docker-compose stack (db + backend + frontend) is up.

    This drives the same containers a developer would run locally with
    `docker compose up` — it does not spin up separate dev servers, so it
    never conflicts with an already-running stack on the same ports.
    """
    subprocess.run(["docker", "compose", "up", "-d"], cwd=REPO_ROOT, check=True)
    _wait_until_up(f"{BACKEND_URL}/openapi.json")
    _wait_until_up(FRONTEND_URL)


@pytest.fixture(scope="session")
def seeded_db(docker_stack):
    env = {**os.environ, "DATABASE_URL": DATABASE_URL}
    subprocess.run(["uv", "run", "python", "seed.py"], cwd=BACKEND_DIR, env=env, check=True)


@pytest.fixture(scope="session")
def base_url(seeded_db):
    """Overrides pytest-playwright's base_url fixture so `page.goto('/...')` works."""
    return FRONTEND_URL


@pytest.fixture()
def seeded_customer():
    """(email, password) for the customer login seed.py creates."""
    return CUSTOMER_EMAIL, CUSTOMER_PASSWORD


@pytest.fixture()
def seeded_admin():
    """(email, password) for the admin login seed.py creates."""
    return ADMIN_EMAIL, ADMIN_PASSWORD

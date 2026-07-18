import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.storage import ensure_bucket
from app.database import create_db_and_tables
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.resources import all_routers
from app.routers.storefront import router as storefront_router
from app.routers.uploads import router as uploads_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    ensure_bucket()
    yield


app = FastAPI(lifespan=lifespan)

# Defaults to localhost/127.0.0.1 for the dev/docker-compose flow; k8s deployments
# override this (e.g. to match a NodePort host) via the ALLOWED_ORIGIN_REGEX env var.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.environ.get(
        "ALLOWED_ORIGIN_REGEX", r"http://(localhost|127\.0\.0\.1):\d+"
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(storefront_router)
app.include_router(chat_router)
app.include_router(uploads_router)

for router in all_routers:
    app.include_router(router)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, SQLModel

from app.core.exceptions import ConflictError, NotFoundError
from app.database import get_session
from app.dependencies import require_role
from app.models import UserRole
from app.repositories import Repository
from app.services import CrudService


def build_crud_router(
    *,
    model: type[SQLModel],
    create_schema: type[SQLModel],
    update_schema: type[SQLModel],
    read_schema: type[SQLModel],
    prefix: str,
    tags: list[str],
    read_roles: list[UserRole] | None = (UserRole.ADMIN, UserRole.STAFF),
    write_roles: list[UserRole] = (UserRole.ADMIN, UserRole.STAFF),
) -> APIRouter:
    """read_roles=None means the read endpoints are public (no auth required)."""
    router = APIRouter(prefix=prefix, tags=tags)
    read_dependencies = [] if read_roles is None else [Depends(require_role(*read_roles))]
    write_dependencies = [Depends(require_role(*write_roles))]

    def get_service(session: Session = Depends(get_session)) -> CrudService:
        return CrudService(Repository(session, model))

    @router.post("", response_model=read_schema, status_code=201, dependencies=write_dependencies)
    def create(item: create_schema, service: CrudService = Depends(get_service)):
        try:
            return service.create(item)
        except ConflictError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("", response_model=list[read_schema], dependencies=read_dependencies)
    def list_all(
        offset: int = 0,
        limit: int = Query(default=100, le=500),
        service: CrudService = Depends(get_service),
    ):
        return service.list(offset=offset, limit=limit)

    @router.get("/{item_id}", response_model=read_schema, dependencies=read_dependencies)
    def get_one(item_id: int, service: CrudService = Depends(get_service)):
        try:
            return service.get(item_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.patch("/{item_id}", response_model=read_schema, dependencies=write_dependencies)
    def update(item_id: int, item: update_schema, service: CrudService = Depends(get_service)):
        try:
            return service.update(item_id, item)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_role(UserRole.ADMIN))])
    def delete(item_id: int, service: CrudService = Depends(get_service)):
        try:
            service.delete(item_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router

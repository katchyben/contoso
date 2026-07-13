from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from database import get_session


def build_crud_router(
    *,
    model: type[SQLModel],
    create_schema: type[SQLModel],
    update_schema: type[SQLModel],
    read_schema: type[SQLModel],
    prefix: str,
    tags: list[str],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.post("", response_model=read_schema, status_code=201)
    def create(item: create_schema, session: Session = Depends(get_session)):
        db_item = model.model_validate(item)
        session.add(db_item)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(exc.orig)) from exc
        session.refresh(db_item)
        return db_item

    @router.get("", response_model=list[read_schema])
    def list_all(
        offset: int = 0,
        limit: int = Query(default=100, le=500),
        session: Session = Depends(get_session),
    ):
        return session.exec(select(model).offset(offset).limit(limit)).all()

    @router.get("/{item_id}", response_model=read_schema)
    def get_one(item_id: int, session: Session = Depends(get_session)):
        db_item = session.get(model, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return db_item

    @router.patch("/{item_id}", response_model=read_schema)
    def update(item_id: int, item: update_schema, session: Session = Depends(get_session)):
        db_item = session.get(model, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        session.add(db_item)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(exc.orig)) from exc
        session.refresh(db_item)
        return db_item

    @router.delete("/{item_id}", status_code=204)
    def delete(item_id: int, session: Session = Depends(get_session)):
        db_item = session.get(model, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        session.delete(db_item)
        session.commit()

    return router

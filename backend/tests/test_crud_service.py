import pytest

from app import models, schemas
from app.core.exceptions import ConflictError, NotFoundError
from app.repositories import Repository
from app.services.crud_service import CrudService


@pytest.fixture()
def service(session):
    return CrudService(Repository(session, models.Category))


def test_create_persists_item(service):
    category = service.create(schemas.CategoryCreate(name="Electronics"))
    assert category.id is not None
    assert category.name == "Electronics"


def test_list_returns_created_items(service):
    service.create(schemas.CategoryCreate(name="Electronics"))
    service.create(schemas.CategoryCreate(name="Home"))
    assert {c.name for c in service.list()} == {"Electronics", "Home"}


def test_get_raises_not_found_for_missing_id(service):
    with pytest.raises(NotFoundError):
        service.get(999999)


def test_update_applies_partial_fields(service):
    category = service.create(schemas.CategoryCreate(name="Electronics"))
    updated = service.update(category.id, schemas.CategoryUpdate(name="Consumer Electronics"))
    assert updated.name == "Consumer Electronics"


def test_update_raises_not_found_for_missing_id(service):
    with pytest.raises(NotFoundError):
        service.update(999999, schemas.CategoryUpdate(name="Whatever"))


def test_delete_removes_item(service):
    category = service.create(schemas.CategoryCreate(name="Electronics"))
    service.delete(category.id)
    with pytest.raises(NotFoundError):
        service.get(category.id)


def test_create_raises_conflict_on_unique_violation(session):
    service = CrudService(Repository(session, models.Product))
    service.create(
        schemas.ProductCreate(sku="SKU-1", name="Widget", unit_price="9.99", stock_quantity=1)
    )
    with pytest.raises(ConflictError):
        service.create(
            schemas.ProductCreate(sku="SKU-1", name="Duplicate SKU", unit_price="9.99", stock_quantity=1)
        )

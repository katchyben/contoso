from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core import storage
from app.core.exceptions import ValidationError
from app.dependencies import require_role
from app.models import UserRole

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", status_code=201, dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.STAFF))])
def upload_image(file: UploadFile = File(...)):
    try:
        url = storage.upload_image(file)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"url": url}

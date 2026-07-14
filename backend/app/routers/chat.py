from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session
from starlette.concurrency import run_in_threadpool

from app import models
from app.core.exceptions import UnauthorizedError
from app.database import get_session
from app.repositories import CustomerRepository, UserRepository
from app.services import AuthService, ChatService

router = APIRouter(tags=["chat"])


def get_ws_customer(
    websocket: WebSocket,
    token: str,
    session: Session = Depends(get_session),
) -> models.Customer:
    auth_service = AuthService(UserRepository(session))
    try:
        user = auth_service.get_current_user(token)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc

    if user.role != models.UserRole.CUSTOMER or user.customer_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    customer = CustomerRepository(session).get(user.customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return customer


@router.websocket("/ws/chat")
async def chat_ws(
    websocket: WebSocket,
    session: Session = Depends(get_session),
    customer: models.Customer = Depends(get_ws_customer),
):
    try:
        chat_service = ChatService(session)
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    await websocket.accept()
    history: list[dict] = []

    try:
        while True:
            user_text = await websocket.receive_text()
            history.append({"role": "user", "content": user_text})
            try:
                reply = await run_in_threadpool(chat_service.reply, customer, history)
            except Exception:
                reply = "Sorry, I'm having trouble answering right now. Please try again in a moment."
            history.append({"role": "assistant", "content": reply})
            await websocket.send_json({"role": "assistant", "content": reply})
    except WebSocketDisconnect:
        pass

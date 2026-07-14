from unittest.mock import patch

from langchain_core.messages import AIMessage


def test_chat_ws_rejects_missing_token(client):
    try:
        with client.websocket_connect("/ws/chat"):
            raise AssertionError("connection should have been rejected")
    except Exception:
        pass


def test_chat_ws_rejects_invalid_token(client):
    denied = False
    try:
        with client.websocket_connect("/ws/chat?token=garbage"):
            pass
    except Exception as exc:
        denied = True
        assert getattr(exc, "status_code", None) == 401
    assert denied


def test_chat_ws_rejects_staff_account(client, make_staff_user, issue_token):
    user, _ = make_staff_user()
    token = issue_token(user)

    denied = False
    try:
        with client.websocket_connect(f"/ws/chat?token={token}"):
            pass
    except Exception as exc:
        denied = True
        assert getattr(exc, "status_code", None) == 403
    assert denied


def test_chat_ws_round_trip_returns_llm_reply(client, make_customer, issue_token):
    _, user, _ = make_customer()
    token = issue_token(user)

    with patch(
        "app.services.chat_service.ChatGoogleGenerativeAI.invoke",
        return_value=AIMessage(content="We have that in stock!"),
    ):
        with client.websocket_connect(f"/ws/chat?token={token}") as ws:
            ws.send_text("Do you have widgets?")
            reply = ws.receive_json()

    assert reply == {"role": "assistant", "content": "We have that in stock!"}


def test_chat_ws_falls_back_gracefully_when_llm_call_fails(client, make_customer, issue_token):
    _, user, _ = make_customer()
    token = issue_token(user)

    with patch(
        "app.services.chat_service.ChatGoogleGenerativeAI.invoke",
        side_effect=RuntimeError("upstream is down"),
    ):
        with client.websocket_connect(f"/ws/chat?token={token}") as ws:
            ws.send_text("Do you have widgets?")
            reply = ws.receive_json()

    assert reply["role"] == "assistant"
    assert "trouble" in reply["content"].lower()

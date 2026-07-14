from playwright.sync_api import Page, expect


def test_chat_widget_round_trip(page: Page, seeded_customer):
    email, password = seeded_customer
    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_text("Catalog")).to_be_visible()

    page.get_by_test_id("chat-toggle").click()
    chat_input = page.get_by_test_id("chat-input")
    expect(chat_input).to_be_enabled(timeout=10000)  # wait for the websocket handshake to complete

    chat_input.fill("Do you have any laptops in stock?")
    chat_input.press("Enter")

    expect(page.get_by_test_id("chat-message-user")).to_contain_text("Do you have any laptops in stock?")
    # Even without a valid LLM key configured, ChatService's fallback path guarantees a reply.
    expect(page.get_by_test_id("chat-message-assistant")).to_be_visible(timeout=20000)


def test_chat_widget_is_hidden_for_anonymous_visitors(page: Page):
    page.goto("/")
    expect(page.get_by_test_id("chat-toggle")).to_have_count(0)

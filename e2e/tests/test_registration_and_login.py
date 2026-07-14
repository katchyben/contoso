import re
import uuid

from playwright.sync_api import Page, expect


def test_new_customer_can_register_sign_out_and_sign_back_in(page: Page):
    email = f"e2e-{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    page.goto("/login")
    page.get_by_role("tab", name="Create account").click()
    page.get_by_label("First name").fill("Eve")
    page.get_by_label("Last name").fill("Tester")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Create account & continue").click()

    expect(page.get_by_text("Catalog")).to_be_visible()
    expect(page.get_by_role("button", name=re.compile(r"^Sign out"))).to_be_visible()

    page.get_by_role("button", name=re.compile(r"^Sign out")).click()
    expect(page.locator('a[href="/login"]')).to_be_visible()

    page.locator('a[href="/login"]').click()
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()

    expect(page.get_by_role("button", name=re.compile(r"^Sign out \(Eve"))).to_be_visible()


def test_register_rejects_duplicate_email(page: Page):
    email = f"e2e-dupe-{uuid.uuid4().hex[:8]}@example.com"

    def register():
        page.goto("/login")
        page.get_by_role("tab", name="Create account").click()
        page.get_by_label("First name").fill("Dupe")
        page.get_by_label("Last name").fill("Customer")
        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").fill("password123")
        page.get_by_role("button", name="Create account & continue").click()

    register()
    expect(page.get_by_text("Catalog")).to_be_visible()
    page.get_by_role("button", name=re.compile(r"^Sign out")).click()

    register()
    expect(page.get_by_role("alert")).to_contain_text("already exists")

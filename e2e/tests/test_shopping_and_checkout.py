import re

from playwright.sync_api import Page, expect


def _sign_in(page: Page, email: str, password: str):
    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_text("Catalog")).to_be_visible()


def test_customer_can_add_to_cart_and_complete_checkout(page: Page, seeded_customer):
    email, password = seeded_customer
    _sign_in(page, email, password)

    page.get_by_role("button", name="Add to cart").first.click()

    page.locator('a[href="/cart"]').click()
    expect(page.get_by_text("Cart", exact=True)).to_be_visible()

    page.get_by_role("button", name="Proceed to checkout").click()
    page.get_by_label("Address line 1").fill("1 Main St")
    page.get_by_label("City").fill("Springfield")
    page.get_by_label("Postal code").fill("00000")
    page.get_by_role("button", name=re.compile(r"Place order")).click()

    expect(page).to_have_url(re.compile(r"/orders/\d+$"))

    page.locator('a[href="/orders"]').click()
    expect(page.get_by_text("My Orders")).to_be_visible()
    expect(page.get_by_role("cell", name=re.compile(r"^WEB-"))).to_be_visible()


def test_cart_page_shows_empty_state_when_no_items(page: Page, seeded_customer):
    email, password = seeded_customer
    _sign_in(page, email, password)

    page.locator('a[href="/cart"]').click()
    expect(page.get_by_text("Your cart is empty")).to_be_visible()

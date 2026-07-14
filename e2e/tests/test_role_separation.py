from playwright.sync_api import Page, expect


def test_admin_route_blocks_customer_accounts(page: Page, seeded_customer):
    email, password = seeded_customer
    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_text("Catalog")).to_be_visible()

    page.goto("/admin")
    expect(page.get_by_text("Customer accounts don't have access to the back office.")).to_be_visible()


def test_admin_login_succeeds_for_admin_account(page: Page, seeded_admin):
    email, password = seeded_admin
    page.goto("/admin")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()

    expect(page.get_by_text("ORDER OPS")).to_be_visible()

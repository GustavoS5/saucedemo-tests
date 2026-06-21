"""Login page object for the saucedemo site."""

from __future__ import annotations

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Represents https://www.saucedemo.com/ — the sign-in screen."""

    url = "/"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error_message = page.get_by_test_id("error")

    def load(self):
        """Navigate to the login page."""
        self.navigate()

    def login(self, username: str, password: str):
        """Fill credentials and submit the login form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error(self) -> str:
        """Return the error message text shown on a failed login."""
        return self.error_message.inner_text()

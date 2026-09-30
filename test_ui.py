import os
import unittest
from playwright.sync_api import sync_playwright

# Target the local server by default, or an external URL if specified
TARGET_URL = os.environ.get("TEST_URL", "http://localhost:8000")

class TestVtabUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        # Run headless by default (no visible browser window), perfect for automated testing
        cls.browser = cls.playwright.chromium.launch(headless=True)
        
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    def test_01_login_page_loads(self):
        """Verify the login page renders correctly with all expected inputs."""
        self.page.goto(f"{TARGET_URL}/login")
        self.assertIn("Sign in", self.page.title())
        self.assertTrue(self.page.locator("h1:has-text('Welcome to Vtab 365')").is_visible())
        self.assertTrue(self.page.locator("input[name='email']").is_visible())
        self.assertTrue(self.page.locator("input[name='password']").is_visible())

    def test_02_invalid_login_shows_error(self):
        """Verify that entering incorrect credentials shows a security flash error."""
        self.page.goto(f"{TARGET_URL}/login")
        self.page.fill("input[name='email']", "fakeuser@vtab.local")
        self.page.fill("input[name='password']", "wrongpassword123")
        self.page.click("button:has-text('Sign in to workspace')")
        
        # The page should gracefully reject the login and display an error
        error_locator = self.page.locator(".flash.error")
        self.assertTrue(error_locator.is_visible())
        self.assertIn("Invalid email or password", error_locator.inner_text())

    def test_03_forgot_password_navigation(self):
        """Verify the forgot password flow is accessible from the login screen."""
        self.page.goto(f"{TARGET_URL}/login")
        self.page.click("a:has-text('Forgot password?')")
        self.assertTrue(self.page.locator("h1:has-text('Forgot Password')").is_visible())
        self.assertTrue(self.page.locator("input[name='email']").is_visible())
        
    def test_04_register_page_loads(self):
        """Verify the employee registration page is functional."""
        self.page.goto(f"{TARGET_URL}/register")
        self.assertIn("Register", self.page.title())
        self.assertTrue(self.page.locator("h1:has-text('Create your Vtab identity')").is_visible())

if __name__ == "__main__":
    print("==================================================")
    print(f"Running VTAB 365 UI Tests against: {TARGET_URL}")
    print("==================================================")
    print("Note: Make sure your server is running before executing this script.")
    print("Requires Playwright: pip install pytest-playwright && playwright install")
    print("--------------------------------------------------")
    unittest.main(verbosity=2)

import os
import time

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


url = os.environ.get('BLS_URL')
class BLSAuthentication:
    def __init__(self):
        """Initializes WebDriver and loads the login page."""
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        # Setup Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

        # Navigate to the login page
        self.driver.get(url)
        time.sleep(2)

    def check_element_state(self, element, element_name):
        """Debug function to check element state (visibility, enabled, etc.)."""
        print(f"\nChecking {element_name}:")
        print(f"Is displayed: {element.is_displayed()}")
        print(f"Is enabled: {element.is_enabled()}")
        print(f"Classes: {element.get_attribute('class')}")
        print(f"Type: {element.get_attribute('type')}")
        print(f"Current value: {element.get_attribute('value')}")

    def make_elements_visible(self):
        """Makes the correct username and password fields visible using JavaScript."""

        self.driver.execute_script("""
            // Show the correct username and password fields
            document.getElementById('UserId3').style.display = 'block';
            document.getElementById('Password2').style.display = 'block';

            // Hide other fields
            Array.from(document.querySelectorAll('input[id^="UserId"')).forEach(el => {
                if(el.id !== 'UserId3') el.style.display = 'none';
            });
            Array.from(document.querySelectorAll('input[id^="Password"')).forEach(el => {
                if(el.id !== 'Password2') el.style.display = 'none';
            });

            // Ensure parent elements are visible
            document.getElementById('UserId3').parentElement.style.display = 'block';
            document.getElementById('Password2').parentElement.style.display = 'block';
        """)

        print("Made elements visible...")

    def fill_credentials(self, username, password):
        """Fills in the username and password using JavaScript."""
        try:
            # Wait until the username and password fields are visible
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.getElementById("UserId3").style.display') == 'block'
            )
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.getElementById("Password2").style.display') == 'block'
            )

            # Locate the fields
            username_field = self.driver.find_element(By.ID, "UserId3")
            password_field = self.driver.find_element(By.ID, "Password2")

            # Focus on the elements and set the values
            self.driver.execute_script("arguments[0].focus();", username_field)
            self.driver.execute_script("arguments[0].focus();", password_field)

            # Fill the credentials
            self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
            self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)

            # Check the element state after filling in the credentials
            self.check_element_state(username_field, "Username field")
            self.check_element_state(password_field, "Password field")

            print("Filled in credentials...")

        except Exception as e:
            print(f"Error occurred while filling credentials: {str(e)}")

    def click_verify_button(self):
        """Waits for and clicks the verify button."""
        try:
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnVerify"))
            )
            verify_button.click()
            print("Clicked verify button...")

        except Exception as e:
            print(f"Error occurred while clicking verify button: {str(e)}")

    def click_login_button(self):
        """Waits for and clicks the login button."""
        try:
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnSubmit"))
            )

            self.check_element_state(login_button, "Login button")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            self.driver.execute_script("arguments[0].disabled = false;", login_button)

            login_button.click()
            print("Clicked login button...")

            WebDriverWait(self.driver, 20).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "overlay-spinner"))
            )
            print("Overlay disappeared or page loaded.")

            self.driver.execute_script("arguments[0].click();", login_button)

            # Wait for a successful login indication or redirection
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "someElementAfterLogin"))  # Replace with an element that appears after login
            )
            print("Page redirected successfully after login.")

        except Exception as e:
            print(f"Error occurred while clicking login button: {str(e)}")


    def login(self):
        username = ""
        password = ""

        try:
            self.make_elements_visible()
            self.fill_credentials(username, password)
            self.click_verify_button()

            time.sleep(40)
            self.click_login_button()
        except Exception as e:
            print(f"Login process failed: {str(e)}")


service = BLSAuthentication()
service.login()


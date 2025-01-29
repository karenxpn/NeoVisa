import os
import time

from fastapi import HTTPException
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
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(url)
        time.sleep(2)

    @staticmethod
    def check_element_state(element, element_name):
        print(f"\nChecking {element_name}:")
        print(f"Is displayed: {element.is_displayed()}")
        print(f"Is enabled: {element.is_enabled()}")
        print(f"Classes: {element.get_attribute('class')}")
        print(f"Type: {element.get_attribute('type')}")
        print(f"Current value: {element.get_attribute('value')}")

    def make_elements_visible(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'UserId')]"))
            )

            # Make fields visible
            self.driver.execute_script("""
                let userField = document.querySelector('input[id^="UserId"]');
                let passField = document.querySelector('input[id^="Password"]');

                if (userField && passField) {
                    userField.style.display = 'block';
                    passField.style.display = 'block';
                    userField.removeAttribute('readonly');
                    passField.removeAttribute('readonly');
                    userField.removeAttribute('disabled');
                    passField.removeAttribute('disabled');
                }
            """)
            print("Fields made visible.")

        except Exception as e:
            raise HTTPException(500, str(e))

    def fill_credentials(self, username, password):
        try:
            # Find all username and password fields
            user_fields = self.driver.find_elements(By.XPATH, "//input[contains(@id, 'UserId')]")
            pass_fields = self.driver.find_elements(By.XPATH, "//input[contains(@id, 'Password')]")

            if not user_fields or not pass_fields:
                raise HTTPException(500, 'Error filling credentials.')

            # Select the first visible and enabled input field
            user_field = next((f for f in user_fields if f.is_displayed() and f.is_enabled()), None)
            pass_field = next((f for f in pass_fields if f.is_displayed() and f.is_enabled()), None)

            if not user_field or not pass_field:
                raise HTTPException(500, 'No usable input fields found.')

            # Fill credentials
            self.driver.execute_script("""
                function simulateUserInput(element, value) {
                    element.focus();
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
                }

                simulateUserInput(arguments[0], arguments[2]);
                simulateUserInput(arguments[1], arguments[3]);
            """, user_field, pass_field, username, password)

            self.check_element_state(user_field, "Active Username Field")
            self.check_element_state(pass_field, "Active Password Field")

        except Exception as e:
            raise HTTPException(500, f"Error filling credentials: {str(e)}")

    def handle_verification(self):
        try:
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnVerify"))
            )
            verify_button.click()
            print("Clicked verify button")

            try:
                submit_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "btnSubmit"))
                )
                submit_button.click()
                print("Clicked submit button")
            except:
                raise HTTPException(500, 'Submit button not found or not needed')

        except Exception as e:
            raise HTTPException(500, f"Error during verification: {str(e)}")

    def login(self):
        try:
            self.make_elements_visible()
            time.sleep(1)
            self.fill_credentials("", "")
            time.sleep(1)
            self.handle_verification()
        except Exception as e:
            raise HTTPException(500, f"Login failed: {str(e)}")
        finally:
            input("Press Enter to continue...")


service = BLSAuthentication()
service.login()
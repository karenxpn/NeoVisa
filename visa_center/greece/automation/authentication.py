import os

from pytesseract import pytesseract
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

url = os.environ.get('GREECE_URL')

class GreeceAuthentication:
    def __init__(self, username, password):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

        service = Service(ChromeDriverManager().install())

        self.url = url
        self.username = username
        self.password = password

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(url)


    def fill_credentials(self):
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-login"))
        )

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        # solve captcha after that click the login button
        login_button.click()


# greece = GreeceAuthentication("", "")
# greece.fill_credentials()
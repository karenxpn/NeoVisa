import os

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

url = os.environ.get('BLS_URL')

class BLSAuthentication:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver.get(url)


BLSAuthentication()


import base64
import io
import re
import time
from io import BytesIO

from PIL import Image
from pytesseract import pytesseract
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import cv2
import numpy as np



class CaptchaSolver:
    def __init__(self, driver):
        self.driver = driver
        self.clicked_images = set()

    def get_captcha_instructions(self):
        time.sleep(7)
        captcha_element = self.driver.find_element(By.ID, 'popup_1')
        captcha_image = captcha_element.screenshot_as_png

        image = Image.open(BytesIO(captcha_image))
        captcha_text = pytesseract.image_to_string(image)

        match = re.search(r'\d+', captcha_text)

        return match.group() if match else None

    def solve_captcha(self, instructions):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
            )

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "captcha-img"))
            )

            # Find all CAPTCHA divs
            captcha_divs = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'padding:5px')]")
            print('captcha_divs:', captcha_divs)

            if not captcha_divs:
                print("No visible CAPTCHA images found.")
            else:
                print(f"Found {len(captcha_divs)} visible CAPTCHA images.")

                for div in captcha_divs:
                    # Get the image element
                    img = div.find_element(By.TAG_NAME, "img")
                    img_src = img.get_attribute("src")

                    if img_src.startswith("data:image/gif;base64,"):
                        print("Processing Base64 CAPTCHA image...")
                        base64_data = img_src.split(",")[1]

                        # Decode and process the image
                        image_data = base64.b64decode(base64_data)
                        image = Image.open(io.BytesIO(image_data))
                        image.show()

                        image_np = np.array(image)
                        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

                        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                        denoised = cv2.fastNlMeansDenoising(binary, None, 30, 7, 21)

                        # Use OCR to extract text from the CAPTCHA image
                        captcha_text = pytesseract.image_to_string(denoised, config="--psm 6 --oem 3").strip()
                        print('captcha_text before regex:', captcha_text)
                        captcha_text = re.sub(r'[^0-9]', '', captcha_text)

                        print(f"Extracted CAPTCHA text: {captcha_text}")

                        # Simulate a click on the image
                        if captcha_text == instructions:
                            is_obstructed = self.driver.execute_script("""
                                var elem = arguments[0];
                                var rect = elem.getBoundingClientRect();
                                var style = window.getComputedStyle(elem);
                                var isObstructed = false;
                                // Check if the element is being overlapped by other elements
                                if (rect.top < 0 || rect.left < 0 || rect.bottom > window.innerHeight || rect.right > window.innerWidth) {
                                    isObstructed = true;
                                }
                                return isObstructed;
                            """, img)

                            if is_obstructed:
                                print("The image is obstructed by another element.")
                            else:
                                # Use JavaScript to click on the image even if it has no size/location
                                img_id = img.get_attribute("src")
                                if img_id not in self.clicked_images:
                                    # Simulate the click using JavaScript
                                    img_width = img.size['width']
                                    img_height = img.size['height']

                                    if img_width > 0 and img_height > 0:
                                        print(f"Image width: {img_width}, height: {img_height}")
                                        ActionChains(self.driver).move_to_element(img).click().perform()
                                        self.clicked_images.add(img_id)  # Mark this image as clicked
                                        print("Clicked on the CAPTCHA image using JavaScript.")
                                    else:
                                        # If the image is invisible or not interactable, try using JavaScript click
                                        self.driver.execute_script("arguments[0].click();", img)
                                        self.clicked_images.add(img_id)
                                        print("Clicked on the CAPTCHA image using JavaScript (fallback).")

                                else:
                                    print("Image has already been clicked.")

            # Locate and click submit button (Modify the selector if necessary)
            # submit_button = WebDriverWait(self.driver, 5).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
            # )
            # submit_button.click()
            print("Submitted CAPTCHA.")

        except Exception as e:
            print(f"An error occurred: {e}")
import asyncio
import base64
import io
import re
import time
from io import BytesIO

from PIL import Image
from pytesseract import pytesseract
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import cv2
import numpy as np



class CaptchaSolver:
    def __init__(self, driver):
        self.driver = driver
        self.clicked_images = set()

    async def get_captcha_instructions(self):
        await asyncio.sleep(4)
        captcha_element = self.driver.find_element(By.ID, 'popup_1')
        captcha_image = captcha_element.screenshot_as_png

        image = Image.open(BytesIO(captcha_image))
        captcha_text = pytesseract.image_to_string(image)

        match = re.search(r'\d+', captcha_text)

        return match.group() if match else None

    async def solve_captcha(self, instructions):
        try:
            await asyncio.to_thread(
                WebDriverWait(self.driver, 10).until,
                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
            )

            await asyncio.to_thread(
                WebDriverWait(self.driver, 10).until,
                EC.presence_of_element_located((By.CLASS_NAME, "captcha-img"))
            )

            captcha_divs = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'padding:5px')]")
            if not captcha_divs:
                print("No visible CAPTCHA images found.")
                return

            tasks = [self.captcha_image_interaction(div, instructions) for div in captcha_divs]
            await asyncio.gather(*tasks)

            # Submit CAPTCHA
            elements = self.driver.find_elements(By.XPATH, "//div[@class='col-4 text-center img-action-div']")
            for index, element in enumerate(elements):
                if "Submit Selection" in element.text:
                    print(f"Clicking element {index}...")
                    await asyncio.to_thread(element.click)
                    break
            print("Submitted CAPTCHA.")

        except Exception as e:
            print(f"An error occurred: {e}")


    async def captcha_image_interaction(self, div, instructions):
        # Get the image element
        img = div.find_element(By.TAG_NAME, "img")
        img_src = img.get_attribute("src")

        if img_src.startswith("data:image/gif;base64,"):
            base64_data = img_src.split(",")[1]
            result = self.preprocess_captcha(base64_data)

            if result == instructions:
                is_obstructed = await asyncio.to_thread(self.driver.execute_script, """
                    var elem = arguments[0];
                    var rect = elem.getBoundingClientRect();
                    var style = window.getComputedStyle(elem);
                    var isObstructed = false;
                    if (rect.top < 0 || rect.left < 0 || rect.bottom > window.innerHeight || rect.right > window.innerWidth) {
                        isObstructed = true;
                    }
                    return isObstructed;
                """, img)

                if not is_obstructed:
                    img_id = img.get_attribute("src")
                    if img_id not in self.clicked_images:
                        # Simulate clicking the image
                        await asyncio.to_thread(self.driver.execute_script, "arguments[0].click();", img)
                        self.clicked_images.add(img_id)
                    else:
                        print("Image has already been clicked.")


    @staticmethod
    def preprocess_captcha(image_data):
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Convert to numpy array
        image_np = np.array(image)

        # Ensure RGB format
        if len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        elif image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)

        # Increase size
        scaled = cv2.resize(image_np, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(scaled, cv2.COLOR_RGB2GRAY)

        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Binary threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

        # Add padding
        padded = cv2.copyMakeBorder(denoised, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

        # Ensure text is black on white background
        if np.mean(padded) < 127:
            padded = cv2.bitwise_not(padded)

        # Try multiple OCR configurations
        configs = [
            '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        ]

        results = []
        for config in configs:
            text = pytesseract.image_to_string(padded, config=config).strip()
            numbers = re.sub(r'[^0-9]', '', text)
            if len(numbers) == 3:  # Only accept 3-digit numbers
                results.append(numbers)

        # Try alternative preprocessing if no valid results
        if not results:
            # Alternative preprocessing with different threshold
            _, binary2 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            denoised2 = cv2.fastNlMeansDenoising(binary2, None, 10, 7, 21)
            padded2 = cv2.copyMakeBorder(denoised2, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

            for config in configs:
                text = pytesseract.image_to_string(padded2, config=config).strip()
                numbers = re.sub(r'[^0-9]', '', text)
                if len(numbers) == 3:
                    results.append(numbers)

        # Return most common 3-digit result
        if results:
            from collections import Counter
            return Counter(results).most_common(1)[0][0]

        return ""
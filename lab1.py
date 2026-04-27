import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageChops
import imagehash

os.makedirs("baselines", exist_ok=True)
os.makedirs("diffs", exist_ok=True)

@pytest.fixture
def browser():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    yield driver
    driver.quit()

def test_python_documentation_vs_downloads(browser):
    browser.get("https://www.python.org")
    wait = WebDriverWait(browser, 15)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    
    docs_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Documentation")))
    docs_link.click()
    time.sleep(2)
    
    docs_screenshot = "baselines/documentation.png"
    browser.get_screenshot_as_file(docs_screenshot)
    
    downloads_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Downloads")))
    downloads_link.click()
    time.sleep(2)
    
    downloads_screenshot = "baselines/downloads.png"
    browser.get_screenshot_as_file(downloads_screenshot)
    
    img_docs = Image.open(docs_screenshot).convert("RGB")
    img_downloads = Image.open(downloads_screenshot).convert("RGB")
    h1 = imagehash.phash(img_docs)
    h2 = imagehash.phash(img_downloads)
    
    diff_path = "diffs/docs_vs_downloads_diff.png"
    
    if (h1 - h2) > 5:
        diff_img = ImageChops.difference(img_docs, img_downloads)
        diff_img.save(diff_path)
        assert False, f'Страницы отличаются! (разница хэшей: {abs(h1 - h2)})'
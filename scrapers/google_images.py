from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests
import os, time
from urllib.parse import quote_plus
from PIL import Image
import io

def fetch_top_images(query, n=5):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = f"https://www.google.com/search?tbm=isch&q={quote_plus(query)}"
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    imgs = soup.find_all("img")
    result = []

    for img in imgs:
        src = img.get("src")
        # Only process http/https URLs, skip base64 and SVGs
        if src and src.startswith("http"):
            try:
                resp = requests.get(src, timeout=5)
                img_data = resp.content
                img_obj = Image.open(io.BytesIO(img_data))
                os.makedirs("static", exist_ok=True)
                filename = os.path.join("static", f"arch_{len(result)}.png")
                img_obj.save(filename, "PNG")
                result.append(filename)
                if len(result) >= n:
                    break
            except Exception as e:
                print(f"Failed to process image: {e}")
                continue
    
    driver.quit()
    return result

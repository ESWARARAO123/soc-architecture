# scraper.py
import os
import requests
from bs4 import BeautifulSoup

def search_and_download_image(query, save_path="assets/arch.png"):
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    img_tags = soup.find_all("img")

    if len(img_tags) > 1:
        img_url = img_tags[1]['src']
        img_data = requests.get(img_url).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        return save_path
    else:
        raise Exception("No image found.")
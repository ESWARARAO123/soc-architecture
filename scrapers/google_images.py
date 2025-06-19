from llm.ollama_handler import ask_text, analyze_image
import tempfile
from urllib.parse import urlparse, parse_qs, quote_plus
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests
import os, time

def fetch_top_images(query, n=5):
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    if not SERPAPI_KEY:
        raise ValueError('SERPAPI_KEY environment variable not set')
    params = {
        'engine': 'google',
        'q': query,
        'tbm': 'isch',
        'api_key': SERPAPI_KEY,
        'ijn': 0
    }
    response = requests.get('https://serpapi.com/search', params=params)
    data = response.json()
    results = []
    seen = set()
    for img in data.get('images_results', []):
        link = img.get('original') or img.get('link')
        if link and link not in seen:
            seen.add(link)
            results.append({'link': link, 'description': img.get('title', 'SerpAPI Image')})
            if len(results) >= n:
                break
    return results

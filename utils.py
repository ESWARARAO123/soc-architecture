# utils.py
import os

def ensure_assets_dir():
    if not os.path.exists("assets"):
        os.makedirs("assets")
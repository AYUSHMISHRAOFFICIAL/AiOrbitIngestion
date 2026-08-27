import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    HF_TOKEN = os.getenv("HF_TOKEN")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    OUTPUT_DIR = "data"
    FINAL_DIR = os.path.join(OUTPUT_DIR, "final")
    RAW_DIR = os.path.join(OUTPUT_DIR, "raw")
    PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")

    MAX_RECORDS_PER_SOURCE = 80
    MAX_PAGES_PER_SOURCE = 5
    HTTP_TIMEOUT = 10
    RETRY_ATTEMPTS = 3
    
    # SSRF Protection Configuration
    ALLOWED_SCHEMES = {"http", "https"}
    MAX_REDIRECTS = 3
    MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10 MB limit

# HostAdvice Web Scraper Configuration
import os

DEFAULT_SITEMAP_URL = "https://hostadvice.com/human-sitemap/"
DEFAULT_HUB_URL = "https://hostadvice.com/tools/web-hosting-comparison/"

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
DEFAULT_CONCURRENCY = 6
DEFAULT_TIMEOUT = 10
DEFAULT_REQUEST_DELAY = 0.2  # seconds between batches

"""Scraper template for MagicBricks / 99acres / Housing.com.

This file is a template and safe-to-run example that does NOT perform live scraping
against any website. It contains best-practice code for session control, user-agent
rotation, Selenium setup, and pagination handling that you can adapt when running
in an environment with proper permissions and rate limits.

To actually scrape, replace the selectors with site-specific values and add
API keys or proxies if required.
"""
from fake_useragent import UserAgent
from time import sleep
from random import uniform, choice
from pathlib import Path
import csv


def get_random_headers():
    ua = UserAgent()
    return {'User-Agent': ua.random}


def backoff_sleep(min_s=1.0, max_s=3.0):
    sleep(uniform(min_s, max_s))


def scrape_example(output_path='data/raw/scraper_example.csv', max_pages=2):
    """Non-operational demo: writes simulated rows showing pagination handling."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['id','title','locality','area_sqft','bhk','rent_per_month','url']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in range(1, max_pages+1):
            print(f"[page {p}] headers: {get_random_headers()['User-Agent'][:60]}...")
            # In a real scraper you'd fetch the page here (requests or Selenium)
            backoff_sleep(0.5, 1.5)
            # Simulate 10 results per page
            for i in range(10):
                writer.writerow({
                    'id': f'sample-{p}-{i}',
                    'title': f'Sample listing {p}-{i}',
                    'locality': choice(['Andheri','Bandra','Powai','Juhu']),
                    'area_sqft': round(uniform(300, 1500),1),
                    'bhk': choice([1,2,3]),
                    'rent_per_month': round(uniform(15000, 120000),2),
                    'url': f'https://example.com/{p}/{i}'
                })


if __name__ == '__main__':
    scrape_example()

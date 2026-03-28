import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def fetch_html(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def extract_content(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')
    # Basic heuristic: get all paragraphs. Often novels put content in <p> tags.
    paragraphs = soup.find_all('p')
    text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    # If <p> didn't yield much, try getting all text and stripping excessive whitespace
    if len(text) < 100:
        main_content = soup.find('main') or soup.find(id=re.compile('content')) or soup.find(class_=re.compile('content'))
        if main_content:
            text = "\n".join([line.strip() for line in main_content.get_text().splitlines() if line.strip()])
    return text

async def scrape_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, url) for url in urls]
        htmls = await asyncio.gather(*tasks)
        
    results = []
    for url, html in zip(urls, htmls):
        content = extract_content(html)
        results.append(content)
    return results

def run_scraper(urls):
    if isinstance(urls, str):
        urls = [urls]
    return asyncio.run(scrape_urls(urls))

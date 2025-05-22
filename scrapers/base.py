import asyncio
import logging
import re
import time
from typing import List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from langdetect import detect

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Get page content with retries and error handling."""
        await self.init_session()
        
        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 403:
                        logger.error(f"Access forbidden for {url} - might be blocked")
                        return None
                    elif response.status == 404:
                        logger.warning(f"Page not found: {url}")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except asyncio.TimeoutError:
                logger.error(f"Timeout on attempt {attempt + 1}/{retries} for {url}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {str(e)}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            continue
        return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Swahili characters
        text = re.sub(r'[^\w\s\u00C0-\u017F]', ' ', text)
        return text.strip()

    def is_swahili(self, text: str) -> bool:
        """Check if text is in Swahili."""
        if not text or len(text.split()) < 5:  # Require at least 5 words
            return False
            
        try:
            return detect(text) == 'sw'
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return False

    def normalize_url(self, url: str) -> str:
        """Normalize URL to absolute path."""
        if not url:
            return ""
        return urljoin(self.base_url, url)

    def debug_html(self, html: str, max_length: int = 1000) -> None:
        """Print HTML for debugging."""
        if not html:
            logger.debug("Empty HTML received")
            return
            
        logger.debug(f"HTML preview (first {max_length} chars):\n{html[:max_length]}")
        
        soup = BeautifulSoup(html, 'html.parser')
        logger.debug(f"Parsed HTML structure:\n{soup.prettify()[:max_length]}")

    async def get_article_links(self) -> List[str]:
        """To be implemented by child classes"""
        raise NotImplementedError

    async def extract_article_text(self, url: str) -> str:
        """To be implemented by child classes"""
        raise NotImplementedError 
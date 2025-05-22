from typing import List
from bs4 import BeautifulSoup

from .base import BaseScraper

class BBCSwahiliScraper(BaseScraper):
    async def get_article_links(self) -> List[str]:
        html = await self.get_page(self.base_url)
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/swahili/' in href:
                links.append(href if href.startswith('http') else f"https://www.bbc.com{href}")
        return list(set(links))

    async def extract_article_text(self, url: str) -> str:
        html = await self.get_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('article')
        if not article:
            return ""
        
        paragraphs = article.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        return self.clean_text(text) 
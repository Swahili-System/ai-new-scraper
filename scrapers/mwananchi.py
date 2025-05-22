from typing import List
from bs4 import BeautifulSoup

from .base import BaseScraper

class MwananchiScraper(BaseScraper):
    async def get_article_links(self) -> List[str]:
        """Get article links from Mwananchi homepage and category pages."""
        links = set()
        
        # Try homepage
        html = await self.get_page(self.base_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            # Look for article links in various containers
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(pattern in href.lower() for pattern in ['/habari/', '/taifa/', '/makala/']):
                    full_url = self.normalize_url(href)
                    if full_url:
                        links.add(full_url)
        
        # Try category pages
        categories = ['/habari/', '/taifa/', '/makala/']
        for category in categories:
            url = self.normalize_url(category)
            html = await self.get_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if any(pattern in href.lower() for pattern in ['/habari/', '/taifa/', '/makala/']):
                        full_url = self.normalize_url(href)
                        if full_url:
                            links.add(full_url)
        
        return list(links)

    async def extract_article_text(self, url: str) -> str:
        """Extract article text from Mwananchi article page."""
        html = await self.get_page(url)
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try different article content selectors
        article = None
        selectors = [
            'section.page-content_mcl.detail-e-content',
            'article',
            'div.article-content',
            'div.story-body',
            'div.content-area',
            'div.entry-content'
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                break
        
        if not article:
            self.debug_html(html)  # Debug if no article found
            return ""
        
        # Extract text from paragraphs
        paragraphs = article.find_all('p')
        if not paragraphs:
            # Try finding text in other elements
            paragraphs = article.find_all(['div', 'span'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower()))
        
        text = ' '.join(p.get_text() for p in paragraphs if p.get_text().strip())
        return self.clean_text(text) 
from typing import List
from bs4 import BeautifulSoup

from .base import BaseScraper

class VOASwahiliScraper(BaseScraper):
    async def get_article_links(self) -> List[str]:
        """Get article links from VOA Swahili homepage."""
        links = set()
        
        # Try homepage
        html = await self.get_page(self.base_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            # Look for article links in various containers
            for a in soup.find_all('a', href=True):
                href = a['href']
                # VOA Swahili articles typically have a numeric ID in the URL
                if '/a/' in href and any(c.isdigit() for c in href):
                    full_url = self.normalize_url(href)
                    if full_url and not full_url.endswith(('.jpg', '.png', '.gif')):
                        links.add(full_url)
        
        return list(links)

    async def extract_article_text(self, url: str) -> str:
        """Extract article text from VOA Swahili article page."""
        html = await self.get_page(url)
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try different article content selectors
        article = None
        selectors = [
            'div.article-content',
            'div.article-body',
            'div.story-body',
            'article',
            'div.content-area',
            'div.article__content'  # New selector
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                break
        
        if not article:
            # Try finding the main content div
            article = soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
        
        if not article:
            self.debug_html(html)  # Debug if no article found
            return ""
        
        # Extract text from paragraphs
        paragraphs = article.find_all('p')
        if not paragraphs:
            # Try finding text in other elements
            paragraphs = article.find_all(['div', 'span'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower()))
        
        # Remove any paragraphs that are likely ads or navigation
        filtered_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 20 and not any(x in text.lower() for x in ['advertisement', 'sponsored', 'click here']):
                filtered_paragraphs.append(text)
        
        text = ' '.join(filtered_paragraphs)
        return self.clean_text(text) 
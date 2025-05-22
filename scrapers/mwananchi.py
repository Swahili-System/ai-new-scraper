from typing import List
from bs4 import BeautifulSoup

from .base import BaseScraper

class MwananchiScraper(BaseScraper):
    async def get_article_links(self) -> List[str]:
        """Get article links from Mwananchi homepage and category pages."""
        links = set()
        
        # Define sections to scrape
        sections = [
            '/habari/',  # General news
            '/taifa/',   # National
            '/makala/',  # Articles
            '/mw/habari/biashara',  # Business
            '/mw/habari/kimataifa', # International
            '/mw/habari/kitaifa'    # National
        ]
        section_roots = [
            '/habari/', '/taifa/', '/makala/',
            '/mw/habari/biashara', '/mw/habari/kimataifa', '/mw/habari/kitaifa'
        ]
        
        for section in sections:
            url = self.normalize_url(section)
            html = await self.get_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # Normalize and check if it's a valid article link
                    full_url = self.normalize_url(href)
                    # Exclude media files
                    if href.endswith(('.jpg', '.png', '.gif', '.mp4', '.pdf')):
                        continue
                    # Must match one of the news section patterns
                    if any(pattern in href for pattern in section_roots):
                        # Exclude root category pages (must be longer than just the section root)
                        if not any(href.rstrip('/').endswith(root.rstrip('/')) and len(href.rstrip('/')) == len(root.rstrip('/')) for root in section_roots):
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
            'div.article-content',
            'section.text-block.blk-txt',
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
        
        # Filter out short paragraphs and ads
        filtered_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 50 and not any(x in text.lower() for x in ['advertisement', 'sponsored', 'click here', 'copyright']):
                filtered_paragraphs.append(text)
        
        text = ' '.join(filtered_paragraphs)
        return self.clean_text(text)

    async def extract_article(self, url: str) -> dict:
        html = await self.get_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        # Headline
        headline_tag = soup.find('h1')
        headline = headline_tag.get_text(strip=True) if headline_tag else ""
        
        # Main text
        article = None
        selectors = [
            'div.article-content',
            'section.text-block.blk-txt',
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
            self.debug_html(html)
            return None
            
        paragraphs = article.find_all('p')
        if not paragraphs:
            paragraphs = article.find_all(['div', 'span'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower()))
            
        # Filter out short paragraphs and ads
        filtered_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 50 and not any(x in text.lower() for x in ['advertisement', 'sponsored', 'click here', 'copyright']):
                filtered_paragraphs.append(text)
                
        text = ' '.join(filtered_paragraphs)
        text = self.clean_text(text)
        
        # Only return if we have substantial content
        if len(text.split()) < 50:  # Require at least 50 words
            return None
            
        # Label based on URL
        label = "news"
        if '/biashara/' in url:
            label = "business"
        elif '/kimataifa/' in url:
            label = "international"
        elif '/kitaifa/' in url:
            label = "national"
            
        # Headline + text
        headline_text = f"{headline} {text}"
        return {
            "label": label,
            "headline": headline,
            "text": text,
            "headline_text": headline_text,
            "url": url
        } 
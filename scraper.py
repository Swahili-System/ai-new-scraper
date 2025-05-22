import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Set, Dict, Any

import aiohttp
from bs4 import BeautifulSoup
from langdetect import detect
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from scrapers import (
    MwananchiScraper
    # HabariLeoScraper,
    # IPPMediaScraper,
    # BBCSwahiliScraper,
    # VOASwahiliScraper
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_page(self, url: str) -> str:
        await self.init_session()
        try:
            async with self.session.get(url) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""

    def clean_text(self, text: str) -> str:
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Swahili characters
        text = re.sub(r'[^\w\s\u00C0-\u017F]', ' ', text)
        return text.strip()

    def is_swahili(self, text: str) -> bool:
        try:
            return detect(text) == 'sw'
        except:
            return False

class DatasetCreator:
    def __init__(self):
        self.scrapers = [
            MwananchiScraper('https://www.mwananchi.co.tz'),
            # HabariLeoScraper('https://www.habarileo.co.tz'),
            # IPPMediaScraper('https://www.ippmedia.com/nipashe'),
            # BBCSwahiliScraper('https://www.bbc.com/swahili'),
            # VOASwahiliScraper('https://www.voaswahili.com')
        ]
        self.articles = []
        self.vectorizer = TfidfVectorizer()

    async def collect_articles(self):
        for scraper in tqdm(self.scrapers, desc="Scrapers"):  # Progress bar for scrapers
            try:
                links = await scraper.get_article_links()
                for link in tqdm(links, desc=f"Articles from {scraper.base_url}"):
                    # Use extract_article for MwananchiScraper
                    if hasattr(scraper, 'extract_article'):
                        article_data = await scraper.extract_article(link)
                        if article_data and article_data["text"] and len(article_data["text"].split()) >= 20 and scraper.is_swahili(article_data["text"]):
                            self.articles.append(article_data)
                    else:
                        text = await scraper.extract_article_text(link)
                        if text and len(text.split()) >= 20 and scraper.is_swahili(text):
                            self.articles.append({
                                "label": "news",
                                "headline": "",
                                "text": text,
                                "headline_text": text,
                                "url": link
                            })
            except Exception as e:
                logger.error(f"Error processing {scraper.base_url}: {str(e)}")
            finally:
                await scraper.close_session()

    def remove_duplicates(self, similarity_threshold: float = 0.8):
        if not self.articles:
            return

        # Convert articles to TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform([a["text"] for a in self.articles])
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find and remove duplicates
        unique_articles = []
        seen_indices = set()
        
        for i in range(len(self.articles)):
            if i in seen_indices:
                continue
                
            unique_articles.append(self.articles[i])
            seen_indices.add(i)
            
            # Find similar articles
            for j in range(i + 1, len(self.articles)):
                if j not in seen_indices and similarity_matrix[i, j] > similarity_threshold:
                    seen_indices.add(j)
        
        self.articles = unique_articles

    def save_dataset(self, output_path: str = "dataset/swahili_news.jsonl"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for article in self.articles:
                json.dump(article, f, ensure_ascii=False)
                f.write('\n')

async def main():
    creator = DatasetCreator()
    await creator.collect_articles()
    creator.remove_duplicates()
    creator.save_dataset()
    logger.info(f"Dataset created with {len(creator.articles)} articles")

if __name__ == "__main__":
    asyncio.run(main()) 
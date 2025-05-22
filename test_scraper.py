import asyncio
import logging
from scrapers import (
    MwananchiScraper,
    HabariLeoScraper,
    IPPMediaScraper,
    BBCSwahiliScraper,
    VOASwahiliScraper
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scraper():
    scrapers = [
        MwananchiScraper('https://www.mwananchi.co.tz'),
        # HabariLeoScraper('https://www.habarileo.co.tz'),
        # IPPMediaScraper('https://www.ippmedia.com/nipashe'),
        # BBCSwahiliScraper('https://www.bbc.com/swahili'),
        # VOASwahiliScraper('https://www.voaswahili.com')
    ]
    
    for scraper in scrapers:
        try:
            logger.info(f"\nTesting {scraper.base_url}")
            logger.info("Fetching article links...")
            links = await scraper.get_article_links()
            
            if links:
                logger.info(f"Found {len(links)} links")
                logger.info(f"Testing first article from {links[0]}")
                
                # Test first article
                text = await scraper.extract_article_text(links[0])
                logger.info(f"Article length: {len(text)} characters")
                logger.info(f"Is Swahili: {scraper.is_swahili(text)}")
                logger.info("First 200 characters: " + text[:200])
            else:
                logger.warning("No links found")
        except Exception as e:
            logger.error(f"Error testing {scraper.base_url}: {str(e)}", exc_info=True)
        finally:
            await scraper.close_session()
            logger.info(f"Completed testing {scraper.base_url}\n")

if __name__ == "__main__":
    logger.info("Starting scraper tests...")
    asyncio.run(test_scraper())
    logger.info("Completed all scraper tests") 
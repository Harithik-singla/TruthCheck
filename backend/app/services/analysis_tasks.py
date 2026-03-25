import time
import asyncio
from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.services.scraper import ArticleScraper, ScraperError

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=2, soft_time_limit=60, time_limit=90)
def run_analysis(self, url: str) -> dict:
    start = time.perf_counter()
    logger.info(f"[Job {self.request.id}] Starting: {url}")

    try:
        scraper = ArticleScraper()
        article = asyncio.run(scraper.scrape(url))
        logger.info(f"[Job {self.request.id}] Scraped: {article.title}")

        # ML steps will be added in Week 2
        duration = time.perf_counter() - start
        return {
            "url": url,
            "title": article.title,
            "credibility_score": 50.0,
            "verdict": "uncertain",
            "claims": [],
            "article_summary": article.text[:300] + "...",
            "processing_time_seconds": round(duration, 2),
        }

    except ScraperError as e:
        logger.error(f"[Job {self.request.id}] Scraper failed: {e}")
        raise self.retry(exc=e, countdown=5)

    except Exception as e:
        logger.error(f"[Job {self.request.id}] Unexpected error: {e}", exc_info=True)
        raise

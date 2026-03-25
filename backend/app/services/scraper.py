import time
from dataclasses import dataclass
from typing import Optional
from newspaper import Article
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapedArticle:
    url: str
    title: str
    text: str
    authors: list[str]
    publish_date: Optional[str]
    scrape_duration_seconds: float


class ScraperError(Exception):
    pass


class PaywallError(ScraperError):
    pass


class ArticleScraper:

    PAYWALL_SIGNALS = [
        "subscribe to read",
        "create a free account",
        "sign in to continue",
        "this content is for subscribers",
    ]
    MIN_ARTICLE_LENGTH = 200

    async def scrape(self, url: str) -> ScrapedArticle:
        start = time.perf_counter()
        logger.info(f"Scraping: {url}")

        try:
            article = await self._scrape_with_newspaper(url)
        except Exception as e:
            logger.warning(f"newspaper3k failed ({e}), trying Playwright...")
            try:
                article = await self._scrape_with_playwright(url)
            except Exception as e2:
                raise ScraperError(f"All scraping strategies failed: {e2}") from e2

        duration = time.perf_counter() - start
        self._validate(article)

        logger.info(f"Scraped '{article.title}' in {duration:.2f}s")
        return ScrapedArticle(
            url=url,
            title=article.title or "Unknown Title",
            text=article.text,
            authors=article.authors,
            publish_date=str(article.publish_date) if article.publish_date else None,
            scrape_duration_seconds=round(duration, 3),
        )

    async def _scrape_with_newspaper(self, url: str) -> Article:
        article = Article(url)
        article.download()
        article.parse()
        return article

    async def _scrape_with_playwright(self, url: str) -> Article:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda r: r.abort())
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            html = await page.content()
            await browser.close()
        article = Article(url)
        article.set_html(html)
        article.parse()
        return article

    def _validate(self, article: Article) -> None:
        text_lower = article.text.lower()
        for signal in self.PAYWALL_SIGNALS:
            if signal in text_lower:
                raise PaywallError(f"Paywall detected: '{signal}'")
        if len(article.text) < self.MIN_ARTICLE_LENGTH:
            raise ScraperError(f"Article too short ({len(article.text)} chars)")

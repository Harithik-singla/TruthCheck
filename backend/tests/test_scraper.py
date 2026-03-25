import pytest
from unittest.mock import MagicMock, patch
from app.services.scraper import ArticleScraper, ScraperError, PaywallError, ScrapedArticle


def make_mock_article(
    title: str = "Test Article",
    text: str = "This is a sufficiently long article text for testing. " * 5,
    authors: list[str] | None = None,
) -> MagicMock:
    mock = MagicMock()
    mock.title = title
    mock.text = text
    mock.authors = authors or ["Test Author"]
    mock.publish_date = None
    return mock


class TestArticleScraper:

    @pytest.fixture
    def scraper(self) -> ArticleScraper:
        return ArticleScraper()

    @pytest.mark.asyncio
    async def test_successful_scrape(self, scraper: ArticleScraper) -> None:
        mock_article = make_mock_article()
        with patch.object(scraper, "_scrape_with_newspaper", return_value=mock_article):
            result = await scraper.scrape("https://example.com/article")
        assert isinstance(result, ScrapedArticle)
        assert result.title == "Test Article"

    @pytest.mark.asyncio
    async def test_paywall_detection(self, scraper: ArticleScraper) -> None:
        mock_article = make_mock_article(text="Subscribe to read the rest of this article. " * 5)
        with patch.object(scraper, "_scrape_with_newspaper", return_value=mock_article):
            with pytest.raises(PaywallError):
                await scraper.scrape("https://example.com/paywalled")

    @pytest.mark.asyncio
    async def test_short_article_raises_error(self, scraper: ArticleScraper) -> None:
        mock_article = make_mock_article(text="Too short.")
        with patch.object(scraper, "_scrape_with_newspaper", return_value=mock_article):
            with pytest.raises(ScraperError):
                await scraper.scrape("https://example.com/empty")

    @pytest.mark.asyncio
    async def test_falls_back_to_playwright(self, scraper: ArticleScraper) -> None:
        mock_article = make_mock_article()
        with patch.object(scraper, "_scrape_with_newspaper", side_effect=Exception("Failed")):
            with patch.object(scraper, "_scrape_with_playwright", return_value=mock_article):
                result = await scraper.scrape("https://example.com/js-heavy")
        assert result.title == "Test Article"

    @pytest.mark.asyncio
    async def test_all_strategies_fail(self, scraper: ArticleScraper) -> None:
        with patch.object(scraper, "_scrape_with_newspaper", side_effect=Exception("Failed")):
            with patch.object(scraper, "_scrape_with_playwright", side_effect=Exception("Also failed")):
                with pytest.raises(ScraperError, match="All scraping strategies failed"):
                    await scraper.scrape("https://example.com/broken")

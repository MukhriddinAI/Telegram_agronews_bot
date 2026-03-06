import logging
import warnings

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")  # suppress SSL warnings for self-signed certs

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10

# RSS feeds (most reliable — structured XML)
UZBEK_RSS_SOURCES = [
    "https://agro-olam.uz/feed/",
    "https://agroxabarlari.uz/feed/",
]

WORLD_RSS_SOURCES = [
    "https://www.agriculturedive.com/feeds/news/",
    "https://igrownews.com/feed/",
]

# HTML sources with <article> tags (no RSS available)
WORLD_HTML_SOURCES = [
    "https://agfundernews.com/",
]


def _get_rss_link(item) -> str:
    """Extract URL from an RSS <item>. Handles text-content and href-attribute variants."""
    link_tag = item.find("link")
    if link_tag:
        text = link_tag.get_text(strip=True)
        if text.startswith("http"):
            return text
        href = link_tag.get("href", "")
        if href.startswith("http"):
            return href
    # Atom <link href="..."/> fallback
    link_tag = item.find("link", href=True)
    if link_tag:
        return link_tag["href"]
    return ""


def _fetch_rss(url: str, group: str, max_articles: int = 5) -> list[dict]:
    """Fetch and parse articles from an RSS/Atom feed."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception as e:
        logger.warning("Failed to fetch RSS %s: %s", url, e)
        return []

    soup = BeautifulSoup(resp.content, "xml")
    articles = []

    for item in soup.find_all("item", limit=max_articles):
        title_tag = item.find("title")
        desc_tag = item.find("description") or item.find("summary")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = _get_rss_link(item)
        if not title or not href:
            continue

        desc = ""
        if desc_tag:
            # Strip any embedded HTML from description
            desc = BeautifulSoup(desc_tag.get_text(strip=True), "html.parser").get_text(strip=True)[:300]
        if not desc:
            desc = title

        articles.append({"sarlavha": title, "mazmun": desc, "url": href, "guruh": group})

    return articles


def _fetch_html(url: str, group: str, max_articles: int = 5) -> list[dict]:
    """Fetch and parse articles from an HTML page using <article> tags."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception as e:
        logger.warning("Failed to fetch HTML %s: %s", url, e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    for el in soup.find_all("article", limit=max_articles * 2):
        heading = el.find(["h1", "h2", "h3", "h4"])
        if not heading:
            continue
        title = heading.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        link_tag = heading.find("a", href=True) or el.find("a", href=True)
        if not link_tag:
            continue
        href = link_tag["href"]
        if not href.startswith("http"):
            continue

        p = el.find("p")
        desc = p.get_text(strip=True)[:300] if p else title

        articles.append({"sarlavha": title, "mazmun": desc, "url": href, "guruh": group})
        if len(articles) >= max_articles:
            break

    return articles


def scrape_agro_news() -> list[dict]:
    """
    Scrape agro news via RSS feeds and HTML article tags.
    Returns a list of dicts: {sarlavha, mazmun, url, guruh}.
    """
    all_articles = []

    for url in UZBEK_RSS_SOURCES:
        articles = _fetch_rss(url, "uzbekiston", max_articles=4)
        logger.info("Scraped %d articles from %s", len(articles), url)
        all_articles.extend(articles)

    for url in WORLD_RSS_SOURCES:
        articles = _fetch_rss(url, "jahon", max_articles=4)
        logger.info("Scraped %d articles from %s", len(articles), url)
        all_articles.extend(articles)

    for url in WORLD_HTML_SOURCES:
        articles = _fetch_html(url, "jahon", max_articles=4)
        logger.info("Scraped %d articles from %s", len(articles), url)
        all_articles.extend(articles)

    logger.info("Total scraped: %d articles", len(all_articles))
    return all_articles

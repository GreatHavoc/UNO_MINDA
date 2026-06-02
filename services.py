"""
services.py
===========
Data-fetching services: news via Google News RSS (with parallel article fetching)
and live stock data via yfinance. All functions return plain Python dicts/lists.
"""

import urllib.parse
import logging
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from googlenewsdecoder import new_decoderv1

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


# ---------------------------------------------------------------------------
# News fetching
# ---------------------------------------------------------------------------

def search_news_direct(topic: str, num: int = 10) -> list[dict]:
    """
    Search for news using Google News RSS.
    Returns a list of article dicts with Google News redirect links.
    """
    results: list[dict] = []
    try:
        query = urllib.parse.quote(topic)
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, headers=_DEFAULT_HEADERS, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        items = root.findall(".//item")
        for item in items[:num]:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")
            source_el = item.find("source")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            pub_date = pub_date_el.text if pub_date_el is not None else ""
            source = source_el.text if source_el is not None else ""

            results.append(
                {
                    "title": title,
                    "url": link,
                    "snippet": "",
                    "source": source,
                    "date": pub_date,
                }
            )
    except requests.exceptions.Timeout:
        logger.warning("Google News RSS search timed out for topic: %s", topic)
        results.append({"error": "Search timed out"})
    except Exception as exc:
        logger.error("Google News RSS search failed for topic %s: %s", topic, exc)
        results.append({"error": f"Search failed: {str(exc)}"})
    return results


def _clean_article_text(text: str) -> str:
    """Remove excessive whitespace and truncate to 5000 characters."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned = "\n\n".join(lines)
    if len(cleaned) > 5000:
        cleaned = cleaned[:5000] + "\n\n... [Article truncated]"
    return cleaned


def fetch_full_article(url: str, timeout: int = 12) -> str:
    """
    Attempt to extract the main article text from a URL.
    Returns the article text, or a bracketed error/status message.
    """
    if not url or not url.startswith("http"):
        return "[Full article unavailable - invalid URL]"

    try:
        resp = requests.get(url, headers=_DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if any(t in content_type for t in ("pdf", "image", "video")):
            return "[Full article is a PDF/media file - cannot extract text]"

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all(
            ["script", "style", "nav", "footer", "header",
             "aside", "iframe", "noscript", "form", "button"]
        ):
            tag.decompose()

        # Strategy 1: <article> tag
        article_tag = soup.find("article")
        if article_tag:
            text = article_tag.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return _clean_article_text(text)

        # Strategy 2: common content class patterns
        keywords = [
            "article-content", "article-body", "article__body", "story-content",
            "story-body", "post-content", "entry-content", "content-body",
            "main-content", "news-content", "articleBody",
        ]
        content_div = soup.find(
            "div",
            class_=lambda x: x and any(k in " ".join(x) for k in keywords),
        )
        if content_div:
            text = content_div.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return _clean_article_text(text)

        # Strategy 3: div with most <p> children
        best_div, max_p = None, 0
        for div in soup.find_all("div"):
            p_count = len(div.find_all("p", recursive=False))
            if p_count > max_p:
                max_p, best_div = p_count, div
        if best_div and max_p >= 3:
            text = "\n\n".join(
                p.get_text(strip=True)
                for p in best_div.find_all("p")
                if p.get_text(strip=True)
            )
            if len(text) > 200:
                return _clean_article_text(text)

        # Strategy 4: all <p> tags
        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 30
        ]
        if paragraphs:
            text = "\n\n".join(paragraphs)
            if len(text) > 200:
                return _clean_article_text(text)

        return "[Full article text could not be extracted from this page]"

    except requests.exceptions.Timeout:
        return "[Full article unavailable - request timed out]"
    except requests.exceptions.ConnectionError:
        return "[Full article unavailable - connection error]"
    except requests.exceptions.HTTPError as exc:
        return f"[Full article unavailable - HTTP {exc.response.status_code}]"
    except Exception as exc:
        logger.error("Article fetch error for %s: %s", url, exc)
        return f"[Full article unavailable - error: {str(exc)[:80]}]"


def _fetch_single_article(item: dict, fetch_articles: bool) -> dict:
    """Helper to resolve and scrape a single article from the Google News RSS item."""
    article_url = item.get("url", "")
    entry = {
        "title": item.get("title", ""),
        "url": article_url,
        "date": item.get("date", ""),
        "snippet": item.get("snippet", "")[:300],
        "source": item.get("source", ""),
    }

    if fetch_articles and article_url:
        try:
            # We resolve the Google News redirect URL to get the target URL first
            decoded = new_decoderv1(article_url, interval=0.1)
            if decoded.get("status"):
                real_url = decoded["decoded_url"]
                entry["url"] = real_url
                entry["full_article"] = fetch_full_article(real_url)
            else:
                entry["full_article"] = f"[Full article unavailable - could not decode URL: {decoded.get('message')}]"
        except Exception as e:
            logger.error("Failed to decode Google News URL %s: %s", article_url, e)
            entry["full_article"] = f"[Full article unavailable - decode error: {str(e)}]"
            
    return entry


def fetch_news(topic: str, num: int = 10, fetch_articles: bool = True) -> list[dict]:
    """
    Fetch news for a topic. Optionally fetches full article content in parallel threads.
    Returns a list of article dicts.
    """
    raw = search_news_direct(topic, num)
    
    # Separate valid items from errors
    valid_items = [item for item in raw if "error" not in item]
    errors = [item for item in raw if "error" in item]

    # Fast path if we aren't fetching full articles or there are no valid items
    if not fetch_articles or not valid_items:
        results = []
        for item in raw:
            if "error" in item:
                results.append(item)
            else:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "date": item.get("date", ""),
                    "snippet": item.get("snippet", "")[:300],
                    "source": item.get("source", ""),
                })
        return results

    # Execute decoding and page fetching in parallel threads
    max_workers = min(len(valid_items), 10)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_fetch_single_article, item, fetch_articles) for item in valid_items]
        results = [future.result() for future in futures]

    return errors + results


# ---------------------------------------------------------------------------
# Stock data
# ---------------------------------------------------------------------------

def fetch_stock_data(ticker_symbol: str) -> dict:
    """
    Fetch stock data for a ticker using yfinance.
    Returns a dict with key financial metrics.
    """
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        prev_close = info.get("previousClose", "N/A")
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")
        revenue = info.get("totalRevenue", "N/A")
        profit_margin = info.get("profitMargins", "N/A")

        if isinstance(market_cap, (int, float)):
            market_cap = f"INR {market_cap / 1e7:.0f} Crore"
        if isinstance(revenue, (int, float)):
            revenue = f"INR {revenue / 1e7:.0f} Crore"

        return {
            "ticker": ticker_symbol,
            "current_price": current_price,
            "prev_close": prev_close,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "revenue_ttm": revenue,
            "profit_margin": (
                f"{profit_margin * 100:.1f}%"
                if isinstance(profit_margin, float)
                else "N/A"
            ),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
    except Exception as exc:
        logger.error("Stock fetch error for %s: %s", ticker_symbol, exc)
        return {"ticker": ticker_symbol, "error": str(exc)}

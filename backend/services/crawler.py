"""Service for crawling and extracting content from websites."""

import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Identify ourselves properly to avoid being blocked by rate-limiting.
USER_AGENT = (
    "AIHiringResearchBot/1.0 "
    "(+https://github.com/ai-developer-hiring; research purposes)"
)


async def crawl_website(url: str, max_pages: int = 3) -> str:
    """Crawl a website and extract text content from up to *max_pages* pages.

    The crawler stays within the same domain and strips non-content elements
    (scripts, styles, nav, footer, aside, header) before extracting text.

    Args:
        url: The starting URL to crawl.
        max_pages: Maximum number of pages to visit.

    Returns:
        A concatenated string of the extracted text from each page.
    """
    visited: set[str] = set()
    to_visit: list[str] = [url]
    content_chunks: list[str] = []
    base_domain = urlparse(url).netloc

    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers=headers,
        timeout=15.0,
    ) as client:
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue

            try:
                logger.info("Crawling page %d/%d: %s", len(visited) + 1, max_pages, current_url)
                response = await client.get(current_url)
                visited.add(current_url)

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove non-content elements
                for tag in soup(["script", "style", "nav", "footer", "aside", "header", "noscript"]):
                    tag.extract()

                text = soup.get_text(separator=" ", strip=True)
                content_chunks.append(f"--- Page: {current_url} ---\n{text[:3000]}")

                # Discover same-domain links
                for link in soup.find_all("a", href=True):
                    next_url = urljoin(current_url, link["href"])
                    parsed = urlparse(next_url)
                    # Only follow same-domain HTTP(S) links
                    if (
                        parsed.netloc == base_domain
                        and parsed.scheme in ("http", "https")
                        and next_url not in visited
                        and next_url not in to_visit
                    ):
                        to_visit.append(next_url)

            except httpx.TimeoutException:
                logger.warning("Timeout while crawling %s", current_url)
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP %d while crawling %s", exc.response.status_code, current_url
                )
            except Exception:
                logger.exception("Unexpected error crawling %s", current_url)

    logger.info("Crawling complete — visited %d page(s)", len(visited))
    return "\n\n".join(content_chunks)

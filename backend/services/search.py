"""Service for performing web searches via the Serper API."""

import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


async def search_company(query: str) -> Dict[str, Any]:
    """Search for a company using the Serper Google Search API.

    Args:
        query: The search query string.

    Returns:
        A dictionary containing the search results, or an error dict.

    Raises:
        httpx.HTTPStatusError: If the Serper API returns a non-2xx status.
        ValueError: If the Serper API key is not configured.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        logger.error("SERPER_API_KEY environment variable is not set")
        raise ValueError("Serper API key not configured")

    logger.info("Searching Serper for query: %s", query)

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            json={"q": query},
        )
        response.raise_for_status()
        results = response.json()
        logger.info(
            "Serper returned %d organic results for query: %s",
            len(results.get("organic", [])),
            query,
        )
        return results

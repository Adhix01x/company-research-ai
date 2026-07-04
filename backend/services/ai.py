"""Service for generating AI-powered structured company research reports."""

import json
import logging
import os
from typing import Any, Dict

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a world-class business and technology analyst. You produce "
    "detailed, structured company research reports in JSON format. "
    "Always respond with valid JSON only — no markdown, no extra text."
)

REPORT_PROMPT_TEMPLATE = """\
Analyze the following company data and competitor intelligence to generate a \
comprehensive structured report.

**Company / Query:** {company_name}

---
### Scraped Website Data
{scraped_data}

---
### Competitor Intelligence
{competitors_data}

---

Return a JSON object with EXACTLY these fields:

{{
  "company_name": "The official company name",
  "website": "The company's official website URL",
  "phone": "Company phone number if found, otherwise 'Not publicly listed'",
  "address": "Company headquarters address if found, otherwise 'Not publicly listed'",
  "summary": "A comprehensive 2-3 paragraph company summary covering mission, founding, and current status",
  "products": ["Product/Service 1", "Product/Service 2", "Product/Service 3"],
  "pain_points": [
    "Specific pain point or challenge the company faces 1",
    "Specific pain point or challenge the company faces 2",
    "Specific pain point or challenge the company faces 3",
    "Specific pain point or challenge the company faces 4"
  ],
  "competitors": [
    {{"name": "Competitor Name 1", "website": "https://competitor1.com"}},
    {{"name": "Competitor Name 2", "website": "https://competitor2.com"}},
    {{"name": "Competitor Name 3", "website": "https://competitor3.com"}},
    {{"name": "Competitor Name 4", "website": "https://competitor4.com"}}
  ]
}}

Requirements:
- products: List 4-6 actual products or services offered by the company
- pain_points: List 3-5 specific, insightful business challenges or pain points
- competitors: List 3-5 real competitors with their actual websites
- summary: Be detailed and specific, not generic
- phone/address: Only include if actually found in the data
- All URLs must be complete (including https://)

Return ONLY valid JSON. No markdown formatting, no code blocks, no explanation.
"""


async def generate_company_report(
    company_name: str,
    scraped_data: str,
    competitors_data: str,
    model: str = "openai/gpt-3.5-turbo",
    api_key: str = "",
) -> Dict[str, Any]:
    """Generate a structured company research report using an LLM.

    Args:
        company_name: Name or query identifying the company.
        scraped_data: Concatenated text scraped from the company website.
        competitors_data: Serialised competitor search results.
        model: The model identifier to use via OpenRouter.
        api_key: OpenRouter API key (overrides env var if provided).

    Returns:
        A dictionary containing the structured report data.

    Raises:
        ValueError: If the OpenRouter API key is not configured.
        Exception: If the LLM request fails.
    """
    resolved_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
    if not resolved_key:
        logger.error("OpenRouter API key not configured")
        raise ValueError("OpenRouter API key not configured. Please provide it in the sidebar settings or set OPENROUTER_API_KEY environment variable.")

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=resolved_key,
    )

    prompt = REPORT_PROMPT_TEMPLATE.format(
        company_name=company_name,
        scraped_data=scraped_data[:8000] if scraped_data else "(no data scraped)",
        competitors_data=competitors_data[:4000] if competitors_data else "(no competitor data available)",
    )

    logger.info("Generating structured report for '%s' using model '%s'", company_name, model)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        raw_text = response.choices[0].message.content
        logger.info("Raw AI response received (%d chars)", len(raw_text))

        # Parse the JSON response
        report = _parse_json_response(raw_text, company_name)
        logger.info("Structured report generated successfully for '%s'", company_name)
        return report

    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI JSON response: %s", e)
        # Return a fallback structured report
        return _fallback_report(company_name, raw_text if 'raw_text' in dir() else "")
    except Exception:
        logger.exception("Failed to generate report for '%s'", company_name)
        raise


def _parse_json_response(text: str, company_name: str) -> Dict[str, Any]:
    """Parse JSON from an AI response, handling various formats."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code blocks
    if "```" in text:
        # Find content between ``` markers
        parts = text.split("```")
        for part in parts:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            if cleaned.startswith("{"):
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue

    # Try finding JSON object in text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse structured JSON — using fallback for '%s'", company_name)
    return _fallback_report(company_name, text)


def _fallback_report(company_name: str, raw_text: str) -> Dict[str, Any]:
    """Generate a fallback structured report when JSON parsing fails."""
    return {
        "company_name": company_name,
        "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
        "phone": "Not publicly listed",
        "address": "Not publicly listed",
        "summary": raw_text[:2000] if raw_text else f"Research data for {company_name} could not be fully structured.",
        "products": ["Core Platform"],
        "pain_points": ["Analysis could not be fully structured — see summary for details."],
        "competitors": [],
    }

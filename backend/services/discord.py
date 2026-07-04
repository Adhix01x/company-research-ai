"""Service for sending rich Discord notifications via webhooks or bot API."""

import logging
import os
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)


def _build_embed(
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str,
    report_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a Discord embed payload for a research report notification.

    Returns:
        A dictionary representing a single Discord embed object.
    """
    summary = report_data.get("summary", "No summary generated.")
    if len(summary) > 600:
        summary = summary[:600] + "..."

    # Format products
    products_list = report_data.get("products", [])
    products_str = "\n".join([f"• {p}" for p in products_list[:5]]) if products_list else "None listed"

    # Format pain points
    pain_points = report_data.get("pain_points", [])
    pain_str = "\n".join([f"• {p}" for p in pain_points[:4]]) if pain_points else "None listed"

    # Format competitors
    competitors = report_data.get("competitors", [])
    comp_str = "\n".join([f"• [{c.get('name')}]({c.get('website')})" for c in competitors[:4] if c.get('name')]) if competitors else "None listed"

    fields = [
        {"name": "👤 Applicant", "value": f"{applicant_name} ({applicant_email})", "inline": False},
        {"name": "🏢 Company", "value": f"**{company_name}**", "inline": True},
        {"name": "🔗 Website", "value": f"[Link]({company_website})" if company_website else "Not listed", "inline": True},
        {"name": "📞 Contact", "value": f"Phone: {report_data.get('phone', 'N/A')}\nAddress: {report_data.get('address', 'N/A')}", "inline": False},
        {"name": "📄 Summary", "value": summary, "inline": False},
        {"name": "🛠️ Products & Services", "value": products_str, "inline": True},
        {"name": "⚠️ Pain Points", "value": pain_str, "inline": True},
        {"name": "⚔️ Competitors", "value": comp_str, "inline": False},
    ]

    return {
        "title": "📊 AI Company Research Report Complete",
        "description": f"Detailed research report generated for **{company_name}**.",
        "color": 0xEAB54D,  # Match the gold accent from the UI
        "fields": fields,
        "footer": {"text": "Company Research AI Assistant"},
    }


async def send_to_discord(
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str,
    report_data: Dict[str, Any],
    bot_token: str = "",
    channel_id: str = "",
) -> bool:
    """Send a rich embedded notification to Discord.

    Supports two modes:
      1. Webhook URL (from env).
      2. Bot token + channel ID (passed from UI or env).

    Args:
        applicant_name: Name of the applicant.
        applicant_email: Email of the applicant.
        company_name: Researched company name.
        company_website: URL of the company website.
        report_data: The structured report data.
        bot_token: Discord bot token (optional).
        channel_id: Discord channel ID (optional).

    Returns:
        True if successful, False otherwise.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    active_bot_token = bot_token or os.getenv("DISCORD_BOT_TOKEN", "")
    active_channel_id = channel_id or os.getenv("DISCORD_CHANNEL_ID", "")

    if not webhook_url and not (active_bot_token and active_channel_id):
        logger.warning("Discord credentials not configured — skipping notification")
        return False

    embed = _build_embed(
        applicant_name, applicant_email, company_name, company_website, report_data
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if webhook_url:
                logger.info("Sending Discord notification via webhook")
                resp = await client.post(webhook_url, json={"embeds": [embed]})
            else:
                logger.info("Sending Discord notification via bot API")
                resp = await client.post(
                    f"https://discord.com/api/v10/channels/{active_channel_id}/messages",
                    headers={"Authorization": f"Bot {active_bot_token}"},
                    json={"embeds": [embed]},
                )
            resp.raise_for_status()
            logger.info("Discord notification sent successfully")
            return True
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Discord API returned HTTP %d: %s",
            exc.response.status_code,
            exc.response.text[:200],
        )
        return False
    except Exception:
        logger.exception("Failed to send Discord notification")
        return False

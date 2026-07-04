"""AI & Automation Developer Hiring API — main application module."""

import logging
import os

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services.ai import generate_company_report
from services.crawler import crawl_website
from services.discord import send_to_discord
from services.pdf import REPORTS_DIR, generate_pdf_report
from services.search import search_company

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI & Automation Developer Hiring API",
    version="2.0.0",
    description="Research companies and generate AI-powered reports with structured data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    """Payload for the /api/research endpoint."""

    company_input: str = Field(
        ..., min_length=1, description="Company name, URL, or search query"
    )
    model: str = Field(
        "openai/gpt-3.5-turbo", description="LLM model identifier for OpenRouter"
    )
    applicant_name: str = Field("", description="Applicant's full name (optional)")
    applicant_email: str = Field("", description="Applicant's email (optional)")

    # API keys from frontend (override env vars if provided)
    serper_api_key: str = Field("", description="Serper.dev API key (optional, overrides env)")
    openrouter_api_key: str = Field("", description="OpenRouter API key (optional, overrides env)")

    # Discord config from frontend
    discord_bot_token: str = Field("", description="Discord bot token (optional)")
    discord_channel_id: str = Field("", description="Discord channel ID (optional)")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health_check():
    """Health-check endpoint for liveness / readiness probes."""
    return {
        "status": "healthy",
        "serper_configured": bool(os.getenv("SERPER_API_KEY")),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "discord_configured": bool(
            os.getenv("DISCORD_WEBHOOK_URL")
            or (os.getenv("DISCORD_BOT_TOKEN") and os.getenv("DISCORD_CHANNEL_ID"))
        ),
    }


@app.post("/api/research")
async def perform_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
):
    """Run a full research pipeline: search → crawl → AI report → PDF.

    Returns the structured report data and a download link for the generated PDF.
    """
    query = request.company_input

    # Resolve API keys: prefer frontend-provided, fallback to env
    serper_key = request.serper_api_key or os.getenv("SERPER_API_KEY", "")
    openrouter_key = request.openrouter_api_key or os.getenv("OPENROUTER_API_KEY", "")
    discord_bot_token = request.discord_bot_token or os.getenv("DISCORD_BOT_TOKEN", "")
    discord_channel_id = request.discord_channel_id or os.getenv("DISCORD_CHANNEL_ID", "")

    # --- Step 1: Search ---
    try:
        search_results = await search_company(query, api_key=serper_key)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Search failed for query '%s'", query)
        raise HTTPException(
            status_code=502, detail=f"Search service error: {exc}"
        )

    # --- Step 2: Determine target URL ---
    target_url = query if query.startswith("http") else None
    if not target_url:
        organic = search_results.get("organic", [])
        if organic:
            target_url = organic[0].get("link")

    if not target_url:
        raise HTTPException(
            status_code=404,
            detail="Could not determine company website URL from the search results.",
        )

    # --- Step 3: Crawl ---
    try:
        scraped_data = await crawl_website(target_url, max_pages=5)
    except Exception as exc:
        logger.exception("Crawling failed for %s", target_url)
        raise HTTPException(
            status_code=502, detail=f"Crawling error: {exc}"
        )

    # --- Step 4: Competitor research ---
    try:
        competitors_search = await search_company(f"{query} competitors", api_key=serper_key)
        competitors_data = str(competitors_search.get("organic", []))
    except Exception:
        logger.warning("Competitor search failed — continuing without it")
        competitors_data = ""

    # --- Step 5: Generate AI report (structured JSON) ---
    try:
        report = await generate_company_report(
            company_name=query,
            scraped_data=scraped_data,
            competitors_data=competitors_data,
            model=request.model,
            api_key=openrouter_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Report generation failed for '%s'", query)
        raise HTTPException(
            status_code=502, detail=f"AI report generation error: {exc}"
        )

    # --- Step 6: Generate PDF from structured data ---
    try:
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in query)
        pdf_filename = f"report_{safe_name}.pdf"
        generate_pdf_report(report, pdf_filename)
    except Exception as exc:
        logger.exception("PDF generation failed")
        raise HTTPException(
            status_code=500, detail=f"PDF generation error: {exc}"
        )

    # --- Step 7: Discord notification (background) ---
    if request.applicant_name and request.applicant_email:
        background_tasks.add_task(
            send_to_discord,
            applicant_name=request.applicant_name,
            applicant_email=request.applicant_email,
            company_name=report.get("company_name", query),
            company_website=report.get("website", target_url),
            report_data=report,
            bot_token=discord_bot_token,
            channel_id=discord_channel_id,
        )

    return {
        "status": "success",
        "target_url": target_url,
        "report": report,
        "pdf_url": f"/api/download_pdf?filename={pdf_filename}",
    }


@app.get("/api/download_pdf")
def download_pdf(filename: str):
    """Download a previously generated PDF report.

    The filename must refer to a file inside the secure reports/ directory.
    Path traversal is prevented by resolving the real path.
    """
    # Sanitize: only use the basename to prevent directory traversal
    safe_name = os.path.basename(filename)
    file_path = os.path.realpath(os.path.join(REPORTS_DIR, safe_name))

    # Ensure the resolved path is still inside REPORTS_DIR
    if not file_path.startswith(os.path.realpath(REPORTS_DIR)):
        logger.warning("Path traversal attempt blocked: %s", filename)
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


# ---------------------------------------------------------------------------
# Serve Frontend Static Files (in Production)
# ---------------------------------------------------------------------------
# Mount the React compiled dist directory at the root "/"
# Check if dist folder exists (it won't exist locally until built)
frontend_dist_dir = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
if os.path.isdir(frontend_dist_dir):
    logger.info("Mounting frontend static files from %s", frontend_dist_dir)
    app.mount("/", StaticFiles(directory=frontend_dist_dir, html=True), name="static")
else:
    logger.warning(
        "Frontend dist directory not found at %s. Serve static files disabled.",
        frontend_dist_dir,
    )


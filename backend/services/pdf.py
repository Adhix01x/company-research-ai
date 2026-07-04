"""Service for generating highly styled professional PDF reports from structured company data."""

import logging
import os
from typing import Any, Dict

from fpdf import FPDF

logger = logging.getLogger(__name__)

# Directory where all generated PDF reports are stored.
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def ensure_reports_dir() -> None:
    """Create the reports directory if it doesn't exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _clean_text(text: str) -> str:
    """Clean unicode characters that are not supported by the default FPDF Latin-1 encoding.

    Replaces smart quotes, en-dashes, em-dashes, and unsupported bullets.
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # Dictionary of common unicode character replacements
    replacements = {
        "\u201c": '"',  # Left curly double quote
        "\u201d": '"',  # Right curly double quote
        "\u2018": "'",  # Left curly single quote
        "\u2019": "'",  # Right curly single quote
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        "\u2022": "*",  # Bullet point
        "\u2026": "...",  # Ellipsis
        "\u00ae": "(R)",  # Registered trademark
        "\u2122": "TM",  # Trademark
        "\u00a0": " ",  # Non-breaking space
        "\u2020": "+",  # Dagger
        "\u2021": "++", # Double dagger
    }

    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)

    # Encode to Win-Ansi (cp1252) / latin-1 and replace unknown characters with '?' to prevent FPDF crash
    return text.encode("latin-1", errors="replace").decode("latin-1")


class CustomPDF(FPDF):
    """Custom FPDF class to add headers, footers, and styling helpers."""

    def header(self):
        # Draw top colored bar
        self.set_fill_color(10, 14, 26)  # Dark Blue-Black
        self.rect(0, 0, 210, 24, "F")
        self.set_fill_color(234, 181, 77)  # Gold Accent
        self.rect(0, 24, 210, 1.5, "F")

        # Header Text
        self.set_font("helvetica", "B", 8)
        self.set_text_color(234, 181, 77)
        self.set_y(8)
        self.cell(0, 10, "COMPANY RESEARCH AI | INTELLIGENCE REPORT", align="C", ln=True)
        self.set_text_color(0, 0, 0)
        self.set_y(32)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # Page number
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf_report(
    report_data: Dict[str, Any],
    filename: str = "report.pdf",
) -> str:
    """Convert structured report data to a beautiful PDF file stored in the reports directory.

    Args:
        report_data: The structured company report data.
        filename: The basename of the output PDF file.

    Returns:
        The absolute path to the generated PDF file.
    """
    ensure_reports_dir()

    # Sanitize filename — only allow the basename, no path traversal
    safe_filename = os.path.basename(filename)
    if not safe_filename.endswith(".pdf"):
        safe_filename += ".pdf"

    output_path = os.path.join(REPORTS_DIR, safe_filename)

    # Extract and clean all text inputs to prevent encoding crashes
    company_name = _clean_text(report_data.get("company_name", "Company Report"))
    website = _clean_text(report_data.get("website", "Not listed"))
    phone = _clean_text(report_data.get("phone", "Not publicly listed"))
    address = _clean_text(report_data.get("address", "Not publicly listed"))
    summary = _clean_text(report_data.get("summary", "No summary available."))
    products = [_clean_text(p) for p in report_data.get("products", [])]
    pain_points = [_clean_text(p) for p in report_data.get("pain_points", [])]
    competitors = report_data.get("competitors", [])

    pdf = CustomPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(15, 30, 15)

    # 1. Title Section
    pdf.set_y(35)
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(15, 21, 37)
    pdf.cell(0, 12, company_name, ln=True)

    # Subtitle link
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(59, 130, 246)  # Accent color
    pdf.cell(0, 8, website, ln=True, link=website)
    pdf.ln(4)

    # 2. Company Metadata Grid
    pdf.set_fill_color(248, 250, 252)  # Very light grey panel
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(15, pdf.get_y(), 180, 24, "FD")

    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 12, "  PHONE:", align="L")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(60, 12, phone, align="L")

    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 12, "ADDRESS:", align="L")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(60, 12, address, align="L", ln=True)
    pdf.ln(8)

    # Section generator helper
    def draw_section_header(title: str, color_rgb=(139, 92, 246)):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*color_rgb)
        pdf.cell(0, 8, title.upper(), ln=True)
        # Line under header
        pdf.set_draw_color(*color_rgb)
        pdf.set_line_width(0.5)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 180, pdf.get_y())
        pdf.ln(6)

    # 3. Overview / Summary
    draw_section_header("1. Company Overview", (59, 130, 246))
    pdf.set_font("helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(180, 6, summary)
    pdf.ln(8)

    # 4. Products & Services
    draw_section_header("2. Key Products & Services", (139, 92, 246))
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    if products:
        for product in products:
            pdf.cell(5, 6, "-", ln=False)  # WinAnsi safe bullet dash
            pdf.multi_cell(175, 6, f" {product}")
    else:
        pdf.cell(0, 6, "No key products or services detected.", ln=True)
    pdf.ln(8)

    # 5. AI-Generated Pain Points
    draw_section_header("3. AI-Generated Pain Points", (234, 181, 77))
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    if pain_points:
        for point in pain_points:
            pdf.cell(5, 6, "-", ln=False)  # WinAnsi safe bullet dash
            pdf.multi_cell(175, 6, f" {point}")
    else:
        pdf.cell(0, 6, "No major pain points detected.", ln=True)
    pdf.ln(8)

    # 6. Competitor Analysis
    draw_section_header("4. Competitor Analysis", (100, 116, 139))
    if competitors:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(15, 21, 37)
        # Header columns
        pdf.cell(90, 6, "Competitor Name", ln=False)
        pdf.cell(90, 6, "Website", ln=True)
        pdf.set_draw_color(226, 232, 240)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 180, pdf.get_y())
        pdf.ln(2)

        pdf.set_font("helvetica", "", 9.5)
        pdf.set_text_color(51, 65, 85)
        for comp in competitors:
            c_name = _clean_text(comp.get("name", "N/A"))
            c_site = _clean_text(comp.get("website", "N/A"))
            pdf.cell(90, 6, c_name, ln=False)
            pdf.set_text_color(59, 130, 246)
            pdf.cell(90, 6, c_site, ln=True, link=c_site)
            pdf.set_text_color(51, 65, 85)
    else:
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, "No direct competitors identified.", ln=True)

    pdf.output(output_path)
    logger.info("Structured PDF report generated successfully at %s", output_path)
    return output_path

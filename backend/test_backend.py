"""Test suite for validating backend research crawling and PDF generation."""

import asyncio
import os
import traceback
from services.crawler import crawl_website
from services.pdf import generate_pdf_report, REPORTS_DIR


async def test_crawler():
    print("=== Testing Crawler ===")
    try:
        data = await crawl_website("https://example.com", max_pages=1)
        if "Example Domain" in data:
            print("✓ Crawler works successfully!")
        else:
            print(f"✗ Crawler failed. Output: {data[:100]}")
    except Exception as exc:
        print(f"✗ Crawler encountered exception: {exc}")


def test_pdf():
    print("=== Testing PDF Generation ===")
    try:
        mock_report_data = {
            "company_name": "Test Company Corp",
            "website": "https://testcompany.com",
            "phone": "+1 (555) 019-2834",
            "address": "123 Innovation Way, Tech City",
            "summary": "This is a test company description for testing backend PDF formatting.",
            "products": ["Cloud Hosting", "AI Infrastructure", "DevOps Pipeline"],
            "pain_points": [
                "Scaling database clusters during traffic bursts.",
                "Reducing latency across multi-region deployments."
            ],
            "competitors": [
                {"name": "Competitor Alpha", "website": "https://alpha.com"},
                {"name": "Competitor Beta", "website": "https://beta.com"}
            ]
        }
        
        pdf_path = generate_pdf_report(mock_report_data, "test_report.pdf")
        if os.path.isfile(pdf_path):
            print(f"✓ PDF report generated successfully at: {pdf_path}")
            os.unlink(pdf_path)
            print("✓ Temporary PDF test file removed.")
        else:
            print("✗ PDF generation failed: File not found.")
    except Exception as exc:
        print("✗ PDF generation encountered exception:")
        traceback.print_exc()


async def main():
    await test_crawler()
    print()
    test_pdf()


if __name__ == "__main__":
    asyncio.run(main())

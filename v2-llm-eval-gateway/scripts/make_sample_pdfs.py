"""Create the 3 small sample PDFs in data/docs/. Run once: python scripts/make_sample_pdfs.py

The documents describe a made-up company ("Acme Store") and were written for this project,
so they are free to share. Replace them with your own PDFs for a real use case.
"""
from pathlib import Path

from fpdf import FPDF

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"

# Each document is a list of pages; each page is a list of paragraphs.
SAMPLE_DOCUMENTS = {
    "refund_policy.pdf": [
        [
            "Acme Store - Refund Policy",
            "Refunds are accepted within 30 days of purchase. A receipt or order number is required.",
            "Items must be returned unused and in their original packaging.",
        ],
        [
            "Exceptions and processing",
            "Digital items (e-books, software licences) cannot be refunded once they have been downloaded.",
            "Approved refunds are paid back to the original payment method within 5 to 7 business days.",
        ],
    ],
    "shipping_guide.pdf": [
        [
            "Acme Store - Shipping Guide",
            "Standard shipping takes 3 to 5 business days and costs $5.",
            "Express shipping takes 1 to 2 business days and costs $15.",
        ],
        [
            "Free and international shipping",
            "Standard shipping is free for orders over $50.",
            "International orders arrive in 7 to 14 business days. Customs fees are paid by the customer.",
        ],
    ],
    "support_handbook.pdf": [
        [
            "Acme Store - Support Handbook",
            "Customer support is open Monday to Friday, 9:00 to 17:00 CET.",
            "Email support answers within 24 hours on working days.",
        ],
        [
            "Premium support and warranty",
            "Premium plan customers get 24/7 phone support.",
            "All hardware products come with a 2-year warranty.",
        ],
    ],
}


# Example: write_pdf(Path("data/docs/refund_policy.pdf"), [["Title", "Paragraph"], ...]) -> creates the file
def write_pdf(pdf_path: Path, pages: list[list[str]]) -> None:
    pdf = FPDF()
    pdf.set_font("Helvetica", size=12)
    for paragraphs in pages:
        pdf.add_page()
        for paragraph in paragraphs:
            pdf.multi_cell(0, 8, paragraph)
            pdf.ln(4)
    pdf.output(str(pdf_path))


if __name__ == "__main__":
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for file_name, pages in SAMPLE_DOCUMENTS.items():
        write_pdf(DOCS_DIR / file_name, pages)
        print(f"Wrote {DOCS_DIR / file_name}")

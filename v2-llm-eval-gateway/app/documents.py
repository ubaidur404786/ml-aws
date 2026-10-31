"""Read PDFs and cut their text into small chunks."""
from pathlib import Path

from pypdf import PdfReader


# Example: read_pdf_pages(Path("data/docs/refund_policy.pdf"))
#   -> [{"text": "Refund Policy. Refunds are accepted within 30 days...", "source": "refund_policy.pdf p.1"}, ...]
def read_pdf_pages(pdf_path: Path) -> list[dict]:
    pages = []
    for page_number, page in enumerate(PdfReader(pdf_path).pages, start=1):
        text = " ".join(page.extract_text().split())  # collapse newlines and extra spaces
        if text:
            pages.append({"text": text, "source": f"{pdf_path.name} p.{page_number}"})
    return pages


# Example: split_into_chunks("one two three four five", chunk_words=3, overlap_words=1)
#   -> ["one two three", "three four five"]
def split_into_chunks(text: str, chunk_words: int = 120, overlap_words: int = 20) -> list[str]:
    words = text.split()
    step = chunk_words - overlap_words
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + chunk_words]))
        if start + chunk_words >= len(words):
            break
    return chunks


# Example: load_chunks(Path("data/docs"))
#   -> [{"text": "Refund Policy. Refunds are accepted...", "source": "refund_policy.pdf p.1"}, ...]
def load_chunks(docs_dir: Path) -> list[dict]:
    chunks = []
    for pdf_path in sorted(docs_dir.glob("*.pdf")):
        for page in read_pdf_pages(pdf_path):
            for chunk_text in split_into_chunks(page["text"]):
                chunks.append({"text": chunk_text, "source": page["source"]})
    return chunks

from pathlib import Path
import fitz  # PyMuPDF
from typing import Dict, Optional, Any

# nomic for embeddings (or replace with GPT4All/Ollama)
from nomic import embed
# from gpt4all import GPT4All
# from ollama import Client


# TODO: Add support for images and formulas in PDFs
# TODO: Update database scheme
# TODO: iwadi find-connections does similarity check between emneddings
def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extracts all text from a PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)


def extract_metadata(pdf_path: Path) -> Dict:
    """Stub for future formula/image parsing or PDF metadata."""
    doc = fitz.open(pdf_path)
    return {
        "title": doc.metadata.get("title", pdf_path.stem),
        "page_count": len(doc),
    }


def generate_embedding(text: str, model: Optional[str] = "nomic-embed-text") -> Any:
    """Generates an embedding vector for the input text using Nomic API (or stub)."""
    res = embed.text(
        texts=[text],
        model=model,
        task_type="search_document",
        dimensionality=768,
    )
    return res["embeddings"][0]

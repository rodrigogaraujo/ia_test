"""CLI script to ingest PDF documents into FAISS vectorstore."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main() -> None:
    from src.config import get_settings
    from src.core.logging import setup_logging
    from src.rag.ingest import build_vectorstore, chunk_documents, extract_pages_with_tables

    settings = get_settings()
    setup_logging(debug=settings.debug)

    pdf_path = os.path.join("data", "manual-politicas-viagem-blis.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    print(f"Extracting pages from {pdf_path}...")
    documents = extract_pages_with_tables(pdf_path)
    print(f"Extracted {len(documents)} pages")

    print(f"Chunking documents (size={settings.chunk_size}, overlap={settings.chunk_overlap})...")
    chunks = chunk_documents(
        documents,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    print(f"Created {len(chunks)} chunks")

    print("Building FAISS vectorstore...")
    build_vectorstore(chunks, settings)
    print(f"Vectorstore saved to {settings.vectorstore_path}")


if __name__ == "__main__":
    main()

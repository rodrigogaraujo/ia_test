"""PDF ingestion pipeline: PDF → chunks → embeddings → FAISS."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pdfplumber
import structlog
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

if TYPE_CHECKING:
    from src.config import Settings

logger = structlog.get_logger()


def extract_pages_with_tables(pdf_path: str) -> list[Document]:
    """Extract text from PDF preserving table structure using pdfplumber."""
    documents = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_number = i + 1
            page_text_parts = []

            # Extract tables and convert to markdown
            tables = page.extract_tables()
            table_regions = []

            for table in tables:
                if not table:
                    continue

                # Convert table to markdown format
                md_rows = []
                for row_idx, row in enumerate(table):
                    cells = [str(cell).strip() if cell else "" for cell in row]
                    md_row = "| " + " | ".join(cells) + " |"
                    md_rows.append(md_row)

                    # Add separator after header
                    if row_idx == 0:
                        separator = "| " + " | ".join(["---"] * len(cells)) + " |"
                        md_rows.append(separator)

                if md_rows:
                    page_text_parts.append("\n".join(md_rows))

            # Extract full page text
            full_text = page.extract_text()
            if full_text:
                # If we have tables, combine table markdown with text
                if page_text_parts:
                    combined = full_text + "\n\n" + "\n\n".join(page_text_parts)
                else:
                    combined = full_text
            else:
                combined = "\n\n".join(page_text_parts) if page_text_parts else ""

            if combined.strip():
                doc = Document(
                    page_content=combined,
                    metadata={
                        "page_number": page_number,
                        "source": os.path.basename(pdf_path),
                        "section": _detect_section(combined),
                    },
                )
                documents.append(doc)

    return documents


def _detect_section(text: str) -> str:
    """Attempt to detect section title from text content."""
    lines = text.strip().split("\n")
    for line in lines[:3]:
        line = line.strip()
        # Look for numbered sections or headers
        if line and len(line) < 100 and not line.startswith("|"):
            return line
    return ""


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Split documents into chunks preserving table integrity."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    return chunks


def build_vectorstore(
    chunks: list[Document],
    settings: Settings,
) -> None:
    """Build FAISS index from document chunks and save to disk."""
    from langchain_community.vectorstores import FAISS

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(settings.vectorstore_path, exist_ok=True)
    vectorstore.save_local(settings.vectorstore_path)
    logger.info(
        "Vectorstore built and saved",
        chunks=len(chunks),
        path=settings.vectorstore_path,
    )

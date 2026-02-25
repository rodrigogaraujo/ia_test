"""RAG retrieval tool wrapping FAISS vectorstore."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS


def create_retriever(vectorstore: FAISS, top_k: int = 5):
    """Create an MMR retriever from the FAISS vectorstore."""
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": top_k,
            "fetch_k": top_k * 5,
            "lambda_mult": 0.6,
        },
    )

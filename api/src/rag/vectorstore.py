"""FAISS vector store setup and persistence."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS

    from src.config import Settings

logger = structlog.get_logger()


def load_vectorstore(settings: Settings) -> FAISS:
    """Load a persisted FAISS vectorstore from disk."""
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings

    index_path = settings.vectorstore_path
    if not os.path.exists(os.path.join(index_path, "index.faiss")):
        raise FileNotFoundError(f"Vectorstore not found at {index_path}")

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    )

    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore


def get_retriever(vectorstore: FAISS, top_k: int = 5):
    """Create an MMR retriever from the vectorstore."""
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": top_k,
            "fetch_k": top_k * 5,
            "lambda_mult": 0.6,
        },
    )

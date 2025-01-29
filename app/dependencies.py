# app/dependencies.py

from fastapi import Depends
from app.retriever import get_hybrid_retriever
from app.retriever import load_and_process_pdf
from langchain.embeddings import HuggingFaceEmbeddings
from typing import Optional
from langchain.schema import Document

# Global variables for reusability
embedder = HuggingFaceEmbeddings()
retriever_instance: Optional[object] = None

def get_retriever() -> object:
    """
    Dependency function to get the retriever instance.
    Ensures retriever is initialized before use.
    
    Returns:
        HybridRetriever: An instance of the hybrid retriever.
    """
    global retriever_instance

    if retriever_instance is None:
        raise ValueError("No retriever available. Upload a document first.")

    return retriever_instance

def update_retriever(pdf_paths: list) -> object:
    """
    Updates the global retriever instance when new PDFs are uploaded.
    
    Args:
        pdf_paths (list): List of PDF file paths to process.
    
    Returns:
        HybridRetriever: Updated retriever instance.
    """
    global retriever_instance

    all_documents = []
    for pdf_path in pdf_paths:
        documents = load_and_process_pdf(pdf_path)
        all_documents.extend(documents)

    if not all_documents:
        raise ValueError("No documents found in uploaded PDFs.")

    retriever_instance = get_hybrid_retriever(all_documents)
    return retriever_instance

import numpy as np
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS 
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_community.document_loaders import PyPDFLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever 
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS
from app.logger_utils import log_performance 

# Initialize the embedding model from config
embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

@log_performance
def load_and_process_pdf(pdf_path: str) -> List[Document]:
    """
    Loads a PDF file, splits it into chunks, and returns processed documents.
    
    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[Document]: List of processed document chunks.
    """
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Split documents into manageable chunks using config values
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return text_splitter.split_documents(docs)

def cosine_similarity(vec1, vec2) -> float:
    """Computes cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@log_performance
def rerank_results(query: str, results: List[Document], embedder: HuggingFaceEmbeddings) -> List[Document]:
    """
    Reranks retrieval results based on similarity to the query.
    
    Args:
        query (str): The input query.
        results (List[Document]): Retrieved documents.
        embedder (HuggingFaceEmbeddings): Embedding model.

    Returns:
        List[Document]: Reranked list of documents.
    """
    query_embedding = embedder.embed_query(query)

    if not results or not hasattr(results[0], "embedding"):
        return results  # Return original results if embeddings are missing

    reranked_results = sorted(
        results,
        key=lambda doc: cosine_similarity(doc.embedding, query_embedding),
        reverse=True
    )
    return reranked_results

@log_performance
def hybrid_with_reranking(
    query: str, 
    bm25: BM25Okapi, 
    faiss_retriever: FAISS, 
    embedder: HuggingFaceEmbeddings, 
    documents: List[Document], 
    top_k: int = TOP_K_RESULTS
) -> List[Document]:
    """
    Performs hybrid retrieval (BM25 + FAISS) and reranks results.

    Args:
        query (str): User query.
        bm25 (BM25Okapi): BM25 retriever.
        faiss_retriever (FAISS): FAISS retriever.
        embedder (HuggingFaceEmbeddings): Embedding model.
        documents (List[Document]): All available documents.
        top_k (int, optional): Number of results to return. Defaults to `TOP_K_RESULTS` from config.

    Returns:
        List[Document]: Reranked retrieved documents.
    """
    if not documents:
        return []

    # Retrieve top BM25 results
    bm25_scores = bm25.get_scores(query.split())
    top_bm25_idx = np.argsort(bm25_scores)[-top_k:]

    # Retrieve top FAISS results
    faiss_results = faiss_retriever.similarity_search(query, k=top_k)

    # Combine BM25 and FAISS results
    combined_results = {doc.metadata.get("source", idx): doc for idx, doc in enumerate(faiss_results)}
    for idx in top_bm25_idx:
        combined_results[documents[idx].metadata.get("source", idx)] = documents[idx]

    combined_docs = list(combined_results.values())

    # Rerank results using cosine similarity
    if combined_docs:
        reranked_docs = rerank_results(query, combined_docs, embedder)
        return reranked_docs[:top_k]
    
    return combined_docs

class HybridRetriever(BaseRetriever, BaseModel):
    """
    Custom retriever that combines BM25 and FAISS for hybrid search.
    """
    documents: List[Document] = Field(..., description="List of documents for retrieval.")
    embedder: HuggingFaceEmbeddings = Field(..., description="Embedding model.")

    bm25: Optional[BM25Okapi] = None
    faiss_retriever: Optional[FAISS] = None

    def __init__(self, **kwargs):
        """
        Initializes the HybridRetriever, setting up BM25 and FAISS.
        """
        super().__init__(**kwargs)

        if not self.documents:
            raise ValueError("No documents provided to initialize HybridRetriever.")

        # Initialize BM25
        tokenized_corpus = [doc.page_content.split(" ") for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # Initialize FAISS
        self.faiss_retriever = FAISS.from_documents(self.documents, self.embedder)

    @log_performance
    def _get_relevant_documents(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Document]:
        """
        Retrieves relevant documents using hybrid search.

        Args:
            query (str): User query.
            top_k (int, optional): Number of documents to return. Defaults to `TOP_K_RESULTS`.

        Returns:
            List[Document]: Retrieved documents.
        """
        return hybrid_with_reranking(query, self.bm25, self.faiss_retriever, self.embedder, self.documents, top_k)

@log_performance
def get_hybrid_retriever(documents: List[Document]) -> HybridRetriever:
    """
    Creates an instance of HybridRetriever.

    Args:
        documents (List[Document]): List of documents to index.

    Returns:
        HybridRetriever: Initialized hybrid retriever.
    """
    if not documents:
        raise ValueError("Cannot create a retriever with an empty document list.")

    return HybridRetriever(documents=documents, embedder=embedder)

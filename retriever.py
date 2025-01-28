import numpy as np
from rank_bm25 import BM25Okapi
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever  # Importing BaseRetriever
from pydantic import BaseModel, Field  # Use Pydantic's BaseModel and Field

# Initialize the embedding model
embedder = HuggingFaceEmbeddings()

def load_and_process_pdf(pdf_path):
    """Loads a PDF, splits it into chunks, and returns processed documents."""
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Split documents into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=150)
    return text_splitter.split_documents(docs)

def cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def rerank_results(query, results, embedder):
    """Reranks retrieval results based on similarity to the query."""
    query_embedding = embedder.embed_query(query)

    if not hasattr(results[0], "embedding"):
        return results  # Return original results if no embeddings

    reranked_results = sorted(
        results,
        key=lambda doc: cosine_similarity(doc.embedding, query_embedding),
        reverse=True
    )
    return reranked_results

def hybrid_with_reranking(query, bm25, faiss_retriever, embedder, documents, top_k=5):
    """Performs hybrid retrieval and reranks results."""
    # Retrieve top BM25 results
    bm25_scores = bm25.get_scores(query.split())
    top_bm25_idx = np.argsort(bm25_scores)[-top_k:]

    # Retrieve top FAISS results
    faiss_results = faiss_retriever.similarity_search(query, k=top_k)

    # Combine BM25 and FAISS results
    combined_results = {doc.metadata.get("source", idx): doc for idx, doc in enumerate(faiss_results)}
    for idx in top_bm25_idx:
        combined_results[documents[idx].metadata.get("source", idx)] = documents[idx]

    # Convert combined results to a list
    combined_docs = list(combined_results.values())

    # Rerank combined results using cosine similarity
    if combined_docs:
        reranked_docs = rerank_results(query, combined_docs, embedder)
        return reranked_docs[:top_k]
    return combined_docs

# Define the HybridRetriever class inheriting from BaseRetriever and Pydantic BaseModel
class HybridRetriever(BaseRetriever, BaseModel):
    """Custom retriever that combines BM25 and FAISS."""
    documents: list[Document] = Field(..., description="List of documents to be used for retrieval.")  # Pydantic field for documents
    embedder: HuggingFaceEmbeddings = Field(..., description="Embedding model for document embeddings.")  # Pydantic field for embedder

    # bm25 and faiss_retriever should be internal variables and not part of the Pydantic validation system
    bm25: BM25Okapi = None
    faiss_retriever: FAISS = None

    def __init__(self, **kwargs):
        # Let Pydantic handle initialization
        super().__init__(**kwargs)  # Initialize the BaseRetriever class

        # Initialize BM25
        tokenized_corpus = [doc.page_content.split(" ") for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # Initialize FAISS
        self.faiss_retriever = FAISS.from_documents(self.documents, self.embedder)

    def _get_relevant_documents(self, query: str, top_k=5):
        """Performs hybrid retrieval and reranks results."""
        return hybrid_with_reranking(query, self.bm25, self.faiss_retriever, self.embedder, self.documents, top_k)

def get_hybrid_retriever(documents):
    """Returns an instance of HybridRetriever."""
    return HybridRetriever(documents=documents, embedder=embedder)

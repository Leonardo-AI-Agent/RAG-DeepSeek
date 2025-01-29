# app/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------
# 🔧 Application Configuration
# -------------------------------

# FastAPI General Settings
APP_NAME = "Hybrid RAG API"
APP_VERSION = "1.0.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Storage Paths
DATA_DIR = os.getenv("DATA_DIR", "data")  # Default folder for storing PDFs
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure directory exists

# -------------------------------
# 🤖 Model & Embeddings Settings
# -------------------------------

# LLM Model Selection
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-r1:1.5b")

# Embedding Model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# -------------------------------
# 🔗 Retrieval System Settings
# -------------------------------

# FAISS & BM25 Configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))  # Default: return top 5 results
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 750))  # Text chunk size
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))  # Overlap to improve retrieval

# -------------------------------
# ⚡ Streaming & Performance
# -------------------------------

STREAMING_DELAY = float(os.getenv("STREAMING_DELAY", 0.02))  # Delay between streamed tokens

# -------------------------------
# 🔐 Security (Optional)
# -------------------------------

# API Key for authentication (Optional)
API_KEY = os.getenv("API_KEY", None)

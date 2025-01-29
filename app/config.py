# app/config.py

import os
from dotenv import load_dotenv
from loguru import logger 

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
# 📝 Logging Configuration (NEW)
# -------------------------------

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/performance.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_ROTATION = os.getenv("LOG_ROTATION", "10MB")  # Rotate logs at 10MB
LOG_RETENTION = os.getenv("LOG_RETENTION", "7")  # Keep logs for 7 days
LOG_FORMAT = os.getenv("LOG_FORMAT", "{time} | {level} | {message}")

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Configure Loguru logger
logger.add(
    LOG_FILE_PATH,
    rotation=LOG_ROTATION,
    retention=f"{LOG_RETENTION} days",
    level=LOG_LEVEL,
    format=LOG_FORMAT
)

logger.info(f"Logging initialized: Writing logs to {LOG_FILE_PATH}")

# -------------------------------
# 🔐 Security (Optional)
# -------------------------------

# API Key for authentication (Optional)
API_KEY = os.getenv("API_KEY", None)

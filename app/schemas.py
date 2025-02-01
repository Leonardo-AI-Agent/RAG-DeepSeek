# app/schemas.py

from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]  # List of source document identifiers

class ThreadedQueryRequest(BaseModel):
    question: str
    # Optional thread_id to specify the thread to query
    thread_id: str = None

class ThreadedQueryResponse(BaseModel):
    answer: str
    thread_id: str
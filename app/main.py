# app/main.py

from fastapi import FastAPI
from app.schemas import ThreadedQueryRequest, ThreadedQueryResponse
import uuid
from app.agent import graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="Hybrid RAG API", version="1.0.0")

@app.post("/query", response_model=ThreadedQueryResponse)
async def query_standard(request: ThreadedQueryRequest):
    print(request)
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    print(thread_id)
    input 
    response = graph.invoke(input={
        "messages": [HumanMessage(content=request.question)],
    }, config={"thread_id": thread_id})
    print(response)

    return ThreadedQueryResponse(answer=response["messages"][-1].content, thread_id=thread_id)

@app.post("/query/stream")
async def query_stream(request: ThreadedQueryRequest):
    print(request)
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    print(thread_id)
    return graph.stream(input={
        "messages": [HumanMessage(content=request.question)],
    }, config={"thread_id": thread_id}, stream_mode='updates')


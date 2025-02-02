# app/main.py

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import uuid

from app.schemas import ThreadedQueryRequest, ThreadedQueryResponse
from app.agent import Agent
from app.config import API_KEY_NAME, API_KEY_PRIVATE

parsed_api_key_name = API_KEY_NAME.replace('\\n', '\n')
parsed_api_key_private = API_KEY_PRIVATE.replace('\\n', '\n')

agent = Agent(
    api_key_name=parsed_api_key_name,
    api_key_private=parsed_api_key_private,
)
app = FastAPI(title="Hybrid RAG API", version="1.0.0")

@app.post("/query", response_model=ThreadedQueryResponse)
async def query_standard(request: ThreadedQueryRequest):
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    user_id = request.user_id if request.user_id else AssertionError("User ID is required")
    response = agent.graph.invoke(input={
        "messages": [HumanMessage(content=request.question)],
        "user_id": user_id
    }, config={"thread_id": thread_id})
    return ThreadedQueryResponse(answer=response["messages"][-1].content, thread_id=thread_id, user_id=user_id)

@app.post("/query/stream")
async def query_stream(request: ThreadedQueryRequest):
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    user_id = request.user_id if request.user_id else AssertionError("User ID is required")
    return agent.graph.stream(input={
        "messages": [HumanMessage(content=request.question)],
        "user_id": user_id
    }, config={"thread_id": thread_id}, stream_mode='updates')
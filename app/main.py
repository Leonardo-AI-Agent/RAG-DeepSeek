# app/main.py

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import uuid

from app.schemas import ThreadedQueryRequest, ThreadedQueryResponse
from app.agent import Agent
from app.config import API_KEY_NAME, API_KEY_PRIVATE
from loguru import logger

# Parse API keys (handling newline escapes)
parsed_api_key_name = API_KEY_NAME.replace('\\n', '\n')
parsed_api_key_private = API_KEY_PRIVATE.replace('\\n', '\n')

# Initialize your agent with API credentials.
agent = Agent(
    api_key_name=parsed_api_key_name,
    api_key_private=parsed_api_key_private,
)
app = FastAPI(title="Hybrid RAG API", version="1.0.0")

@app.post("/query", response_model=ThreadedQueryResponse)
async def query_standard(request: ThreadedQueryRequest):
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    
    # Call the persistent memory chain integrated in the agent.
    answer = agent.handle_query_with_memory(request.question)
    
    return ThreadedQueryResponse(
        answer=answer,
        thread_id=thread_id,
        user_id=request.user_id
    )

@app.post("/query/stream")
async def query_stream(request: ThreadedQueryRequest):
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    
    # Streaming endpoint (uses existing graph-based streaming)
    return agent.graph.stream(
        input={
            "messages": [HumanMessage(content=request.question)],
            "user_id": request.user_id
        },
        config={"thread_id": thread_id},
        stream_mode='updates'
    )

# --- Custom Endpoint for Memory Inspection ---
router = APIRouter()

@router.get("/memory")
async def inspect_memory():
    """
    Returns the persistent conversation memory (chat history) for debugging.
    This endpoint is for testing purposes only.
    """
    try:
        # Ensure the agent's persistent QA chain exists.
        if not hasattr(agent, "qa_chain"):
            # If not, create it (should normally be initialized in the agent constructor).
            agent.qa_chain = agent.handle_query_with_memory("")
            logger.info("Persistent QA chain was not found; re-created it.")

        memory = agent.qa_chain.memory
        chat_history = memory.chat_memory.messages  # This should be a list of messages.
        logger.info("Inspecting memory, chat history: {}", chat_history)
        # Return the chat history as a list of strings.
        return {"chat_history": [str(msg) for msg in chat_history]}
    except Exception as e:
        logger.error("Error inspecting memory: {}", e)
        raise HTTPException(status_code=500, detail="Error retrieving memory")

app.include_router(router)

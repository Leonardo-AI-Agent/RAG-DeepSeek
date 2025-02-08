# app/agent.py

from operator import add
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from uuid import uuid4
from cdp import Cdp, Wallet
from loguru import logger

# Import configuration strings from app/agent_config.py
from app.agent_config import (
    search_instructions,
    generate_instructions,
    restyling_instructions,
    generate_3d_image_prompt_instructions,
    generate_3d_object_prompt_instructions,
    router_instructions,
    wallet_router_instructions
)

# Use absolute imports for services (services is at the project root level)
from services.agent_management import AgentManagementService
from services.persistent_rag import create_qa_chain, handle_query
from langchain.callbacks.manager import CallbackManager
from services.event_callback import CustomEventHandler

class AgentState(MessagesState):
    context: str
    image_prompt: Annotated[list[str], add]
    images_generated: Annotated[list[str], add]
    object_prompt: Annotated[list[str], add]
    objects_generated: Annotated[list[str], add]
    wallet_id: str
    user_id: str
    transaction: any
    response: str

class RouterQuery(BaseModel):
    route: str = Field(None, description="Route to take.")

class SearchQuery(BaseModel):
    query: str = Field(None, description="Search query.")

class Agent:
    def response_router(self, state: AgentState):
        """Route the response based on context."""
        user_id = state.get("user_id", None)
        logger.info("User ID: {}", user_id)
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(RouterQuery)
        response = structured_llm.invoke([SystemMessage(content=router_instructions)] + state['messages'])
        if response.route == "search_web":
            return "search_web"
        elif response.route == "generate_response":
            return "generate_response"
        elif response.route == "generate_3d_image":
            return "generate_3d_image"
        elif response.route == "get_wallet":
            return "get_wallet"
        return "generate_response"

    def search_web(self, state: AgentState):
        """Retrieve docs from web search."""
        llm = ChatOpenAI(model="gpt-4o")
        llm_with_structured_output = llm.with_structured_output(SearchQuery)
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        search_query = search_instructions.format(date=today)
        response = llm_with_structured_output.invoke([SystemMessage(content=search_query)] + state['messages'])
        tavily_search = TavilySearchResults(max_results=3)
        search_docs = tavily_search.invoke(response.query)
        formatted_search_docs = "\n\n---\n\n".join(
            [f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>' for doc in search_docs]
        )
        return {"context": [formatted_search_docs]}

    def generate_response(self, state: AgentState):
        """Generate response with event callbacks and persistent memory."""
        logger.info("Generating response")
        logger.info("Messages: {}", ', '.join([message.content for message in state['messages']]))
        context = state.get("context", "")
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        system_message = generate_instructions.format(context=context, date=today)
        callback_manager = CallbackManager(handlers=[CustomEventHandler()])
        llm = ChatOpenAI(model="gpt-4o", callback_manager=callback_manager)
        response = llm.invoke([SystemMessage(content=system_message)] + state['messages'])
        logger.info("Last response: {}", response.content)
        return {"response": response.content}

    def restyle_response(self, state: AgentState):
        """Restyle response."""
        logger.info("Restyling response")
        system_message = restyling_instructions
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke([SystemMessage(content=system_message)] + [state['response']])
        logger.info("Last response: {}", response.content)
        return {"messages": [response]}

    def generate_3d_image(self, state: AgentState):
        """Generate a 3D image."""
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_image_prompt_instructions.format(messages=state["messages"])
        response = llm.invoke([SystemMessage(content=system_message)] +
                              [HumanMessage(content="Generate a 3D image prompt")])
        return {"image_prompt": [response], "image_generated": [], "messages": [AIMessage(content="3D image generated")]}

    def generate_3d_object(self, state: AgentState):
        """Generate a 3D object."""
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_object_prompt_instructions.format(
            messages=state["messages"], image_prompt=state["image_prompt"]
        )
        response = llm.invoke([SystemMessage(content=system_message)] +
                              [HumanMessage(content="Generate a 3D object prompt")])
        return {"object_prompt": [response], "object_generated": [], "messages": [AIMessage(content="3D object generated")]}

    def create_wallet(self, state: AgentState):
        """Create a wallet."""
        return self.agent_service.create_wallet(state)

    def get_wallet(self, state: AgentState):
        """Retrieve wallet info."""
        return self.agent_service.get_wallet(state)

    def retrieve_wallet_data(self, state: AgentState):
        return self.agent_service.retrieve_wallet_data(state)

    def wallet_router(self, state: AgentState):
        """Route wallet-related responses."""
        return self.agent_service.wallet_router(state)

    def create_transaction(self, state: AgentState):
        """Create a transaction."""
        return self.agent_service.create_transaction(state)

    def handle_query_with_memory(self, query: str, use_summary: bool = False, user_id: str = None):
        """
        Processes a query using the persistent QA chain.
        The chain is created once in __init__ and re-used, so conversation history accumulates.
        """
        result = self.qa_chain.invoke({"query": query})
        if isinstance(result, dict):
            return result.get("result", str(result))
        return str(result)


    def __init__(self, api_key_name: str, api_key_private: str):
        """
        Initialize the agent with API credentials and persistent QA chain.
        """
        self.api_key_name = api_key_name
        self.api_key_private = api_key_private
        self.mongodb_client = MongoClient('mongodb://localhost:27017/')
        self.saver = MongoDBSaver(self.mongodb_client, "agents")
        self.wallets_collection = self.mongodb_client.get_database("agent_wallets").get_collection("wallets")
        self.wallets_collection.create_index("user_id", unique=True)

        logger.info("Initializing agent...")
        logger.info("API Key Name: {}", api_key_name)
        logger.info("API Key Private: {}", api_key_private)

        # Initialize CDP SDK.
        Cdp.configure(self.api_key_name, self.api_key_private)

        # Initialize the Agent Management Service.
        from services.agent_management import AgentManagementService
        self.agent_service = AgentManagementService(self.wallets_collection)

        # Initialize persistent QA chain once for memory persistence.
        self.qa_chain = create_qa_chain()
        
        # Define your workflow graph (existing code)...
        workflow = StateGraph(AgentState)
        workflow.add_node("search_web", self.search_web)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("generate_3d_image", self.generate_3d_image)
        workflow.add_node("generate_3d_object", self.generate_3d_object)
        workflow.add_node("get_wallet", self.get_wallet)
        workflow.add_node("create_wallet", self.create_wallet)
        workflow.add_node("retrieve_wallet_data", self.retrieve_wallet_data)
        workflow.add_node("create_transaction", self.create_transaction)
        workflow.add_node("restyle_response", self.restyle_response)

        workflow.add_conditional_edges(START, self.response_router,
                                       ["search_web", "generate_response", "generate_3d_image", "get_wallet"])
        workflow.add_conditional_edges("get_wallet", self.wallet_router,
                                       ["create_wallet", "create_transaction", "retrieve_wallet_data", "generate_response"])
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_3d_image", "generate_3d_object")
        workflow.add_edge("generate_3d_object", "generate_response")
        workflow.add_edge("create_wallet", "get_wallet")
        workflow.add_edge("create_transaction", "generate_response")
        workflow.add_edge("retrieve_wallet_data", "generate_response")
        workflow.add_edge("generate_response", "restyle_response")
        workflow.add_edge("restyle_response", END)

        self.graph = workflow.compile(checkpointer=self.saver)
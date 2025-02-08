from operator import add
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
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

# Import all instruction strings from agent_config.py
from .agent_config import (
    search_instructions,
    generate_instructions,
    restyling_instructions,
    generate_3d_image_prompt_instructions,
    generate_3d_object_prompt_instructions,
    router_instructions,
    wallet_router_instructions
)

class Transaction:
    def __init__(self, _from: str, _to: str, _amount: str, _data: str):
        self._from = _from
        self._to = _to
        self._amount = _amount
        self._data = _data

class AgentState(MessagesState):
    context: str
    image_prompt: Annotated[list[str], add]
    images_generated: Annotated[list[str], add]
    object_prompt: Annotated[list[str], add]
    objects_generated: Annotated[list[str], add]
    wallet_id: str
    user_id: str
    transaction: Transaction
    response: str

class RouterQuery(BaseModel):
    route: str = Field(None, description="Route to take.")

class SearchQuery(BaseModel):
    query: str = Field(None, description="Search query.")

class Agent:
    def response_router(self, state: AgentState):
        """ Route the response based on the context """
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
        """ Retrieve docs from web search """
        llm = ChatOpenAI(model="gpt-4o")
        llm_with_structured_output = llm.with_structured_output(SearchQuery)
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        search_query = search_instructions.format(date=today)
        response = llm_with_structured_output.invoke([SystemMessage(content=search_query)] + state['messages'])
        
        tavily_search = TavilySearchResults(max_results=3)
        search_docs = tavily_search.invoke(response.query)

        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )

        return {"context": [formatted_search_docs]} 

    def generate_response(self, state: AgentState):
        """ Generate response """
        logger.info("Generating response")
        logger.info("Messages: {}", ', '.join([message.content for message in state['messages']]))

        context = state.get("context", "")
        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        system_message = generate_instructions.format(context=context, date=today)
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke([SystemMessage(content=system_message)] + state['messages'])

        logger.info("Last response: {}", response.content)

        return {"response": response.content}

    def restyle_response(self, state: AgentState):
        """ Restyle response """
        logger.info("Restyling response")

        system_message = restyling_instructions
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke([SystemMessage(content=system_message)] + [state['response']])

        logger.info("Last response: {}", response.content)

        return {"messages": [response]}

    def generate_3d_image(self, state: AgentState):
        """ Generate a 3D image """
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_image_prompt_instructions.format(messages=state["messages"])
        response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate a 3D image prompt")])

        return {"image_prompt": [response], "image_generated": [], "messages": [AIMessage(content="3D image generated")]}

    def generate_3d_object(self, state: AgentState):
        """ Generate a 3D object """
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_object_prompt_instructions.format(messages=state["messages"], image_prompt=state["image_prompt"])
        response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate a 3D object prompt")])

        return {"object_prompt": [response], "object_generated": [], "messages": [AIMessage(content="3D object generated")]}

    def create_wallet(self, state: AgentState):
        """ Create a wallet """
        wallet_document = self.wallets_collection.find_one(filter={"user_id": state.get("user_id", None)})
        if wallet_document:
            return {"messages": [AIMessage(content="Wallet already exists")]}

        user_id = state.get("user_id", str(uuid4()))
        logger.info("User ID: {}", user_id)
        network_id = "base-sepolia"
        logger.info("Network ID: {}", network_id)
        wallet = Wallet.create(network_id=network_id)
        logger.info("Created wallet with ID: {}", wallet.id)

        addresses = [address.address_id for address in wallet.addresses]
        result = self.wallets_collection.insert_one(document={
            "_id": wallet.id,
            "user_id": user_id,
            "wallet_id": wallet.id,
            "network_id": wallet.network_id,
            "addresses": addresses,
        })
        logger.info("Wallet created: {}", result.inserted_id)

        return {"wallet_id": wallet.id, "messages": [AIMessage(content=f"Wallet created: {wallet.addresses[0].address_id}")]}

    def get_wallet(self, state: AgentState):
        """ Get wallet """
        logger.info("Getting wallet")
        user_id = state.get("user_id", None)
        if not user_id:
            raise AssertionError("User ID is required")
        wallet_document = self.wallets_collection.find_one(filter={"user_id": user_id})
        wallet_id = None
        if wallet_document:
            wallet_document_id = wallet_document.get("_id", None)
            logger.info("Wallet Document ID: {}", wallet_document_id)
            if wallet_document_id:
                wallet = Wallet.fetch(wallet_document_id)
                if wallet:
                    wallet_id = wallet.id
                    return {"wallet_id": wallet_id, "messages": [AIMessage(content=f"Wallet found: {wallet.addresses[0]}")]}
        return {"wallet_id": wallet_id, "messages": [AIMessage(content="Wallet not found")]}

    def retrieve_wallet_data(self, state: AgentState):
        if state.wallet_id:
            wallet = Wallet.fetch(state.wallet_id)
            addresses_joined = ', '.join(str(address.address_id) for address in wallet.addresses)
            context_str = (
                f"wallet_id: {wallet.wallet_id}, "
                f"address_id: {wallet.address_id}, "
                f"network_id: {wallet.network_id}, "
                f"addresses: {addresses_joined}"
            )
            return {"context": context_str}

    def wallet_router(self, state: AgentState):
        """ Route the response based on the context """
        logger.info("Wallet Router")
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(RouterQuery)

        wallet_id = state.get("wallet_id", None)
        logger.info("Wallet ID: {}", wallet_id)
        messages = [SystemMessage(content=wallet_router_instructions)] + state['messages']
        logger.info("Messages: {}", ', '.join([message.content for message in messages]))
        response = structured_llm.invoke(messages)

        if response.route == "create_wallet":
            return "create_wallet"
        elif response.route == "create_transaction":
            return "create_transaction"
        elif response.route == "retrieve_wallet_data":
            return "retrieve_wallet_data"
        elif response.route == "generate_response":
            return "generate_response"

    def create_transaction(self, state: AgentState):
        """ Create a transaction """
        wallet_id = state.get("wallet_id", None)
        logger.info("Creating transaction for wallet: {}", wallet_id)
        wallet = Wallet.fetch(wallet_id)

        _from = wallet.addresses[0].address_id
        _to = "0x123456789"
        _amount = "100"
        _data = "0x"

        transaction = Transaction(_from=_from, _to=_to, _amount=_amount, _data=_data)
        return {"messages": [AIMessage(content=f"Transaction created: From {_from} to {_to} with amount {_amount} and data {_data}")]}

    def __init__(self, api_key_name: str, api_key_private: str):
        """
        Initialize the CDPAgentkitClient with API credentials.
        
        :param api_key_name: The API key ID (public identifier).
        :param api_key_private: The API key secret (used for authentication).
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

        # Initialize CDP SDK
        Cdp.configure(self.api_key_name, self.api_key_private)

        # Define a new graph
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

        # Set the entrypoint as conversation
        workflow.add_conditional_edges(START, self.response_router, ["search_web", "generate_response", "generate_3d_image", "get_wallet"])
        workflow.add_conditional_edges("get_wallet", self.wallet_router, ["create_wallet", "create_transaction", "retrieve_wallet_data", "generate_response"])
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_3d_image", "generate_3d_object")
        workflow.add_edge("generate_3d_object", "generate_response")
        workflow.add_edge("create_wallet", "get_wallet")
        workflow.add_edge("create_transaction", "generate_response")
        workflow.add_edge("retrieve_wallet_data", "generate_response")
        workflow.add_edge("generate_response", "restyle_response")
        workflow.add_edge("restyle_response", END)

        # Compile the graph with checkpointing
        self.graph = workflow.compile(checkpointer=self.saver)

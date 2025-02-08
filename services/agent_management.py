# services/agent_management.py

from datetime import datetime
from uuid import uuid4
from loguru import logger
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from cdp import Wallet
from pydantic import BaseModel, Field

# Use absolute import from the app package.
from app.agent_config import (
    generate_3d_image_prompt_instructions,
    generate_3d_object_prompt_instructions,
    wallet_router_instructions
)

class RouterQuery(BaseModel):
    route: str = Field(None, description="Route to take.")

class AgentManagementService:
    def __init__(self, wallets_collection):
        self.wallets_collection = wallets_collection

    def generate_3d_image(self, state):
        """Generate a 3D image prompt."""
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_image_prompt_instructions.format(messages=state["messages"])
        response = llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content="Generate a 3D image prompt")
        ])
        return {
            "image_prompt": [response],
            "image_generated": [],
            "messages": [AIMessage(content="3D image generated")]
        }

    def generate_3d_object(self, state):
        """Generate a 3D object prompt."""
        llm = ChatOpenAI(model="gpt-4o")
        system_message = generate_3d_object_prompt_instructions.format(
            messages=state["messages"], image_prompt=state["image_prompt"]
        )
        response = llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content="Generate a 3D object prompt")
        ])
        return {
            "object_prompt": [response],
            "object_generated": [],
            "messages": [AIMessage(content="3D object generated")]
        }

    def create_wallet(self, state):
        """Create a wallet."""
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
        result = self.wallets_collection.insert_one({
            "_id": wallet.id,
            "user_id": user_id,
            "wallet_id": wallet.id,
            "network_id": wallet.network_id,
            "addresses": addresses,
        })
        logger.info("Wallet created: {}", result.inserted_id)
        return {
            "wallet_id": wallet.id,
            "messages": [AIMessage(content=f"Wallet created: {wallet.addresses[0].address_id}")]
        }

    def get_wallet(self, state):
        """Retrieve wallet information."""
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
                    return {
                        "wallet_id": wallet_id,
                        "messages": [AIMessage(content=f"Wallet found: {wallet.addresses[0]}")]
                    }
        return {"wallet_id": wallet_id, "messages": [AIMessage(content="Wallet not found")]}

    def retrieve_wallet_data(self, state):
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

    def wallet_router(self, state):
        """Route wallet-related responses."""
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

    def create_transaction(self, state):
        """Create a transaction."""
        wallet_id = state.get("wallet_id", None)
        logger.info("Creating transaction for wallet: {}", wallet_id)
        wallet = Wallet.fetch(wallet_id)
        _from = wallet.addresses[0].address_id
        _to = "0x123456789"
        _amount = "100"
        _data = "0x"
        return {
            "messages": [
                AIMessage(content=f"Transaction created: From {_from} to {_to} with amount {_amount} and data {_data}")
            ]
        }

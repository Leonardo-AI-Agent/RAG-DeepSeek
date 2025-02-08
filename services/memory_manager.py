from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.llms import OpenAI
from loguru import logger

class MemoryManager:
    """
    MemoryManager encapsulates LangChain memory objects.
    
    It supports either:
        - "buffer" memory: keeps a complete log of the conversation (ConversationBufferMemory).
        - "summary" memory: summarizes prior interactions to control token usage (ConversationSummaryMemory).
    
    The memory object can be attached to your LLM chain or agent so that context is automatically maintained.
    """
    def __init__(self, memory_type: str = "buffer", max_token_limit: int = 1024):
        self.memory_type = memory_type
        if memory_type == "buffer":
            self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
            logger.info("Initialized ConversationBufferMemory")
        elif memory_type == "summary":
            # Ensure you configure an LLM for summarization (using OpenAI as an example here)
            self.llm = OpenAI(temperature=0)
            self.memory = ConversationSummaryMemory(llm=self.llm, memory_key="history", max_token_limit=max_token_limit)
            logger.info("Initialized ConversationSummaryMemory")
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")

    def get_memory(self):
        """Return the underlying memory object."""
        return self.memory

    def reset_memory(self):
        """Clear the memory's contents."""
        self.memory.clear()
        logger.info("Memory has been reset")

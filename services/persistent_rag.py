import warnings
# (Optional) Suppress memory deprecation warnings if you’re not ready to migrate fully.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.memory")

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA

def create_qa_chain(documents=None, use_summary: bool = False, max_token_limit: int = 1024):
    """
    Create and return a RetrievalQA chain with persistent conversation memory.
    If no documents are provided, a default Leonardo AI–specific corpus is used.
    """
    if documents is None:
        texts = [
            "Leonardo AI is a cutting-edge platform for web3 gaming, crypto, and 3D content creation that empowers creators and developers with advanced AI capabilities.",
            "The platform integrates state-of-the-art language models with modular chain architectures, persistent memory, and retrieval augmented generation to deliver personalized, context-aware interactions.",
            "Leonardo AI leverages seamless wallet integration via the Coinbase Developer Platform (CDP), robust event logging with loguru, and dynamic content generation for both text and 3D assets.",
            "With a focus on equitable access to AI tools and community-driven innovation, Leonardo AI continuously refines its prompt engineering and memory summarization strategies based on user feedback and real-time data."
        ]
        documents = [Document(page_content=text) for text in texts]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts([doc.page_content for doc in documents], embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # Create a ChatMessageHistory instance and persistent memory.
    history = ChatMessageHistory()
    memory = ConversationBufferMemory(chat_memory=history, memory_key="chat_history")

    llm = ChatOpenAI(model="gpt-4o")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        memory=memory
    )
    return qa_chain

def handle_query(query: str, use_summary: bool = False) -> str:
    qa_chain = create_qa_chain(use_summary=use_summary)
    result = qa_chain.invoke({"query": query})
    # If the result is a dict, try to extract a key that contains the answer.
    if isinstance(result, dict):
        return result.get("result", str(result))
    return str(result)

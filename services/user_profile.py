# persistent_rag.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain.schema import Document

def create_qa_chain(documents=None, use_summary: bool = False, max_token_limit: int = 1024):
    """
    Create and return a RetrievalQA chain with persistent conversation memory.
    If use_summary is True, ConversationSummaryMemory is used; otherwise, ConversationBufferMemory.
    """
    if documents is None:
        texts = [
            "Leonardo AI is a cutting-edge platform for web3 gaming, crypto, and 3D content creation that empowers creators and developers with advanced AI capabilities.",
            "The platform integrates state-of-the-art language models with modular chain architectures, persistent memory, and retrieval augmented generation to deliver personalized, context-aware interactions.",
            "Leonardo AI leverages seamless wallet integration via the Coinbase Developer Platform (CDP), robust event logging with loguru, and dynamic content generation for both text and 3D assets.",
            "With a focus on equitable access to AI tools and community-driven innovation, Leonardo AI continuously refines its prompt engineering and memory summarization strategies based on user feedback and real-time data."
        ]
        documents = [Document(page_content=text) for text in texts]

    # Initialize the embedding model and vector store.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts([doc.page_content for doc in documents], embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # Choose memory type.
    llm = ChatOpenAI(model="gpt-4o")
    if use_summary:
        memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", max_token_limit=max_token_limit)
    else:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Create and return the RetrievalQA chain.
    qa_chain = RetrievalQA(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return qa_chain

def handle_query(query: str, use_summary: bool = False) -> str:
    qa_chain = create_qa_chain(use_summary=use_summary)
    return qa_chain.run(query)

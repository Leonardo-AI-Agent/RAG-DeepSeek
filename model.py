from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory  # Importing memory module
from callback_handler import StreamlitCallbackHandler  # Import the callback handler

# Initialize Ollama with the DeepSeek R1 model
llm = Ollama(model="deepseek-r1:1.5b")

# Define the QA prompt
QA_PROMPT = PromptTemplate.from_template("""
1. Use the following context to answer the question.
2. If you don't know, say "I don't know."
3. Keep the answer within 3-4 sentences.

Context: {context}
Question: {query}
Helpful Answer:
""")

def get_qa_chain(retriever):
    """Returns a conversational QA chain with memory."""

    # Initialize memory to store the conversation history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm_chain = LLMChain(llm=llm, prompt=QA_PROMPT, memory=memory)

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
    )

    return RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        input_key="query",  # Define the input key explicitly
        output_key="result",  # Define the output key explicitly
        return_source_documents=True,
        memory=memory  # Attach memory to the RetrievalQA chain
    )

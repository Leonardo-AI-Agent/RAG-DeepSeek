from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
from callback_handler import StreamlitCallbackHandler  # Import the callback handler

# Initialize Ollama with the DeepSeek R1 model
llm = Ollama(model="deepseek-r1:1.5b")

# Define the QA prompt
QA_PROMPT = PromptTemplate.from_template("""
1. Use the following context to answer the question.
2. If you don't know, say "I don't know."
3. Keep the answer within 3-4 sentences.

Context: {context}
Question: {question}
Helpful Answer:
""")

def get_qa_chain(retriever):
    """Returns a conversational QA chain."""
    llm_chain = LLMChain(llm=llm, prompt=QA_PROMPT)
    
    document_prompt = PromptTemplate(
        input_variables=["page_content", "source"],
        template="Context:\ncontent:{page_content}\nsource:{source}",
    )

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
    )

    return RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        return_source_documents=True
    )

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA

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
    """Returns a conversational QA chain."""
    llm_chain = LLMChain(llm=llm, prompt=QA_PROMPT)

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
    )

    return RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        input_key="query",  # Explicitly define input key for the query
        output_key="result",  # Explicitly define output key for the result
        return_source_documents=True
    )

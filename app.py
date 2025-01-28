import streamlit as st
from retriever import load_and_process_pdf, get_hybrid_retriever  # Correct import
from model import get_qa_chain
from utils import save_uploaded_file
from dotenv import load_dotenv
import os
from langchain_core.tracers.context import tracing_v2_enabled  # Import tracing context manager

# Load environment variables
load_dotenv()

# Fetch LangSmith API key
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
if not LANGSMITH_API_KEY:
    st.error("LangSmith API key not found. Please add it to the .env file.")

st.set_page_config(page_title="Hybrid RAG System with LangSmith Tracing", layout="wide")
st.title("🚀 Hybrid RAG with BM25 & FAISS + LangSmith Tracing")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Save uploaded file
    save_path = save_uploaded_file(uploaded_file)

    # Process the PDF
    documents = load_and_process_pdf(save_path)

    # **Call the function** to get the retriever instance
    retriever = get_hybrid_retriever(documents)

    # Initialize the QA chain
    qa_chain = get_qa_chain(retriever)

    # User input
    user_input = st.text_input("Ask a question:")

    if user_input:
        with st.spinner("Processing..."):
            # Enable LangSmith tracing
            with tracing_v2_enabled(project_name="Hybrid_RAG_with_LangSmith"):
                # Retrieve relevant documents
                context_data = retriever._get_relevant_documents(user_input)

                # Prepare the correct dictionary for input variables
                input_data = {
                    "context": "\n".join([doc.page_content for doc in context_data]),  # Combine context into a single string
                    "query": user_input  # User query
                }

                # Use invoke() to handle multiple output keys
                response = qa_chain.invoke(input_data)  # Use the invoke method for LangChain

                # Extract and display the result and source documents
                result = response.get("result", "No result found.")
                source_documents = response.get("source_documents", [])

                st.write("Response:", result)
                st.write("Source Documents:")
                for doc in source_documents:
                    st.write(doc.page_content)

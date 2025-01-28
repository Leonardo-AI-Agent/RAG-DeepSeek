import streamlit as st
from retriever import load_and_process_pdf, get_hybrid_retriever  # Correct import
from model import get_qa_chain
from utils import save_uploaded_file
from langchain.embeddings import HuggingFaceEmbeddings

st.set_page_config(page_title="Hybrid RAG System", layout="wide")
st.title("🚀 Hybrid RAG with BM25 & FAISS")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Save uploaded file
    save_path = save_uploaded_file(uploaded_file)

    # Process the PDF
    documents = load_and_process_pdf(save_path)

    # **Call the function** to get the retriever instance
    retriever = get_hybrid_retriever(documents)  # Correctly calling the function to get retriever instance

    # Initialize the QA chain
    qa_chain = get_qa_chain(retriever)

    # User input
    user_input = st.text_input("Ask a question:")

    if user_input:
        with st.spinner("Processing..."):
            # Retrieve relevant documents using the retriever's _get_relevant_documents method
            context_data = retriever._get_relevant_documents(user_input)  # Retrieve relevant docs using the correct method

            # Prepare the correct dictionary for input variables
            input_data = {
                "context": context_data,  # Add the context from retriever
                "query": user_input       # Change 'question' to 'query' as per LangChain's expectations
            }

            # Use invoke() to handle multiple output keys
            response = qa_chain.invoke(input_data)  # Changed run() to invoke()

            # Extract and display the result and source documents
            result = response.get("result", "No result found.")
            source_documents = response.get("source_documents", [])

            st.write("Response:", result)
            st.write("Source Documents:", source_documents)

import os
import streamlit as st
from retriever import load_and_process_pdf, get_hybrid_retriever
from model import get_qa_chain
from utils import save_uploaded_file

# Ensure the 'data' directory exists
os.makedirs("data", exist_ok=True)

st.set_page_config(page_title="Hybrid RAG System", layout="wide")
st.title("🚀 Hybrid RAG with BM25 & FAISS")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_documents = []

    for uploaded_file in uploaded_files:
        # Save uploaded file with the original filename in the 'data' directory
        file_path = os.path.join("data", uploaded_file.name)
        save_uploaded_file(uploaded_file, file_path)

        # Process the PDF
        documents = load_and_process_pdf(file_path)
        all_documents.extend(documents)

    # **Call the function** to get the retriever instance
    retriever = get_hybrid_retriever(all_documents)  # Pass all combined documents to the retriever

    # Initialize the QA chain
    qa_chain = get_qa_chain(retriever)

    # User input
    user_input = st.text_input("Ask a question:")

    if user_input:
        with st.spinner("Processing..."):
            # Retrieve relevant documents using the retriever's _get_relevant_documents method
            context_data = retriever._get_relevant_documents(user_input)

            # Prepare the correct dictionary for input variables
            input_data = {
                "context": "\n".join([doc.page_content for doc in context_data]),
                "query": user_input,
            }

            # Use the `__call__` method of the chain to process inputs
            response = qa_chain(input_data)

            # Extract and display the result and source documents
            result = response.get("result", "No result found.")
            source_documents = response.get("source_documents", [])

            st.write("Response:", result)
            st.write("Source Documents:")
            for doc in source_documents:
                st.write(doc.page_content)

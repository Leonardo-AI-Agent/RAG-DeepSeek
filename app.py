import streamlit as st
from retriever import load_and_process_pdf, get_hybrid_retriever
from model import get_qa_chain
from utils import save_uploaded_file

# Function to clean invalid characters
def clean_text(text):
    """Removes or replaces invalid characters from a string."""
    return text.encode("utf-8", "ignore").decode("utf-8")

st.set_page_config(page_title="Hybrid RAG System with Memory", layout="wide")
st.title("🚀 Hybrid RAG with BM25 & FAISS + Memory")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Save uploaded file
    save_path = save_uploaded_file(uploaded_file)

    # Process the PDF
    documents = load_and_process_pdf(save_path)

    # **Call the function** to get the retriever instance
    retriever = get_hybrid_retriever(documents)

    # Initialize the QA chain with memory
    qa_chain = get_qa_chain(retriever)

    # User input
    user_input = st.text_input("Ask a question:")

    if user_input:
        with st.spinner("Processing..."):
            # Retrieve relevant documents using the retriever's method
            context_data = retriever._get_relevant_documents(user_input)

            # Clean retrieved context and user input
            cleaned_context = "\n".join([clean_text(doc.page_content) for doc in context_data])
            cleaned_user_input = clean_text(user_input)

            # Prepare the correct dictionary for input variables
            input_data = {
                "query": cleaned_user_input,  # Use cleaned user query
                "context": cleaned_context   # Use cleaned context
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

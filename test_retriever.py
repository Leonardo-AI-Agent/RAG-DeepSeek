from retriever import load_and_process_pdf, get_hybrid_retriever

# Path to your test PDF file
test_pdf_path = "test.pdf"

# Load and process the test PDF
documents = load_and_process_pdf(test_pdf_path)

# Initialize the hybrid retriever
retriever = get_hybrid_retriever()

# Test query
query = "What is RAG?"

# Retrieve the top-3 relevant documents
top_docs = retriever(query, top_k=3)

# Print the results
print("Query:", query)
print("Top Relevant Documents:")
for doc in top_docs:
    print("-", doc.page_content)

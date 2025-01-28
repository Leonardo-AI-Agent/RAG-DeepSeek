# Hybrid RAG System

This project is a Retrieval-Augmented Generation (RAG) system implemented using Python, LangChain, and the DeepSeek R1 model. It combines traditional retrieval techniques (BM25) with modern dense embeddings (FAISS) to build a highly efficient document retrieval and question-answering system.

---

## Features

### Current Features

1. **Hybrid Retrieval**: Combines BM25 and FAISS for robust and accurate document retrieval.
2. **Multi-PDF Support**: Users can upload multiple PDF files for processing, which are stored in a dedicated `data/` directory.
3. **Streamlit UI**: A user-friendly interface for uploading files, asking questions, and viewing results.
4. **Tracing and Analytics**: Integrated tracing with LangSmith to analyze performance and monitor usage.
5. **Custom LLM Integration**: Uses the DeepSeek R1 model (via Ollama) for question answering.
6. **Dynamic Context Handling**: Automatically handles and prepares context for queries.

### Planned Features

#### Enhanced Memory Features

1. **Context-Aware Memory**: Implement dynamic context retention to remember the flow of conversations.
   - Framework: LangChain's updated `ConversationBufferMemory` or `EntityMemory`.
   - Use Case: Retaining context across multiple user queries for more coherent interactions.
2. **User-Specific Memory**: Allow memory reset or persistence for different users.
   - Framework: Redis or PostgreSQL for memory persistence across sessions.

#### File Management

1. **Support for Multiple File Formats**:
   - Additional Formats: Microsoft Word, CSV, and image files (via Tesseract or Amazon Textract for OCR).
   - Library: `python-docx` for Word, `pandas` for CSV, and `pytesseract` or AWS Textract for images.
2. **File Listing UI**:
   - Feature: A sidebar UI for managing uploaded files (view/delete).
   - Library: Streamlit components (`st.sidebar` and `st.selectbox`).

#### Advanced Tracing and Analytics

1. **Usage Analytics**:
   - Framework: LangSmith or OpenTelemetry.
   - Metrics: Number of queries, response times, and user feedback.
2. **Error Logging**:
   - Framework: Sentry or Python's built-in `logging` library.
   - Storage: Centralized logs for troubleshooting.

#### API Integration

1. **REST API**:
   - Framework: FastAPI for building a RESTful API.
   - Use Case: Exposing functionalities for external applications.

#### Security Enhancements

1. **Access Control**:
   - Framework: FastAPI Users for authentication and role-based access.
   - Feature: Secure endpoints for API access.
2. **Data Encryption**:
   - Library: `cryptography` for encrypting files and query results.

#### Enhanced Retrieval

1. **Advanced Retrieval Techniques**:
   - Framework: DPR (Dense Passage Retrieval) using Hugging Face models.
   - Improvement: Replace FAISS with Weaviate or Milvus for better vector storage and search.
2. **Semantic Clustering**:
   - Library: Scikit-learn for clustering similar documents.

#### Performance Optimization

1. **Parallel Processing**:
   - Framework: `concurrent.futures` or `multiprocessing`.
   - Use Case: Faster processing of large files.
2. **Caching System**:
   - Library: Redis or Memcached for caching embeddings and document chunks.

#### Feedback System

1. **User Feedback Loop**:
   - Framework: Streamlit widgets for rating responses.
   - Use Case: Improve system accuracy with user feedback.
2. **Interactive Debugging**:
   - Feature: Flag incorrect answers directly from the UI.

#### Testing and CI/CD

1. **Automated Testing**:
   - Framework: Pytest for unit and integration tests.
   - CI Tool: GitHub Actions for continuous integration.
2. **Continuous Deployment**:
   - Tool: Docker and AWS CodePipeline for seamless updates.

#### Community Engagement

1. **Knowledge Base**:
   - Platform: GitBook or ReadTheDocs for user and developer documentation.
   - Content: Guides, FAQs, and tutorials.
2. **Open Source Contribution**:
   - Platform: GitHub for hosting and collaboration.
   - Feature: Contributor guidelines and issues for community involvement.

---

## Installation

### Prerequisites

- Python 3.9+
- Pip
- Ollama installed ([installation guide](https://www.ollama.com)).

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/hybrid-rag.git
   cd hybrid-rag
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv rag_env
   source rag_env/bin/activate  # On Windows: rag_env\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Ollama and pull the DeepSeek R1 model:

   ```bash
   # Install Ollama
   brew install ollama  # macOS

   # Pull the DeepSeek R1 model
   ollama pull deepseek-r1:1.5b
   ```

5. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. Upload one or more PDF files via the Streamlit UI.
2. Ask questions based on the uploaded documents.
3. View responses and source documents.

---

## Contributing

We welcome contributions! Please check the [Contributing Guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## References

- [LangChain Documentation](https://docs.langchain.com/)
- [DeepSeek R1 Model](https://www.ollama.com)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [BM25](https://pypi.org/project/rank-bm25/)

# Hybrid RAG System with Memory

This project is a **Hybrid Retrieval-Augmented Generation (RAG) System** powered by **BM25** and **FAISS**, allowing for efficient information retrieval and question answering on uploaded documents. The system is integrated with a language model and designed to handle PDF uploads, dynamic memory, and real-time tracing for debugging and analytics.

---

## Features

1. **Multi-Document Upload**: Upload multiple PDF files and store them in a designated `data/` directory.
2. **Efficient Retrieval**: Hybrid scoring using BM25 and FAISS ensures accurate document retrieval.
3. **Conversational QA**: Ask questions about the uploaded files and receive relevant, concise answers.
4. **Dynamic Context Management**: Flexible context retention for improved conversational memory.
5. **Tracing and Debugging**: Integrated LangSmith tracing for monitoring and debugging.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Pip package manager
- An `.env` file with the following variables:
  ```plaintext
  OPENAI_API_KEY=<your_openai_api_key>
  LANGSMITH_API_KEY=<your_langsmith_api_key>
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## TODO: Planned Improvements

### 1. **Enhanced Memory Features**

#### **Context-Aware Memory**

- **Description**: Implement dynamic context retention to remember the flow of conversations over multiple queries.
- **Implementation**: Leverage LangChain's `ConversationBufferMemory` or `ConversationSummaryMemory`.
- **References**: [LangChain Memory Docs](https://python.langchain.com/docs/modules/memory/)

#### **User-Specific Memory**

- **Description**: Allow memory to reset or persist for different users to personalize the interaction.
- **Implementation**: Introduce user session identifiers and associate memory objects with users.

---

### 2. **File Management**

#### **Multiple File Formats**

- **Description**: Support additional file types like Word documents, CSVs, or images (via OCR for text extraction).
- **Implementation**: Use libraries such as `python-docx` (for Word), `pandas` (for CSV), and `pytesseract` (for OCR).

#### **File Listing UI**

- **Description**: Add a sidebar in the UI to list all uploaded files and allow users to delete or view them.
- **Implementation**: Extend the Streamlit UI to include file management options.

---

### 3. **Advanced Tracing and Analytics**

#### **Usage Analytics**

- **Description**: Track the number of queries, response times, and user feedback.
- **Implementation**: Integrate with LangSmith or set up a custom analytics service using `Flask` and `SQLite`.

#### **Error Logging**

- **Description**: Store errors in a centralized log for easier debugging.
- **Implementation**: Use Python's `logging` library and set up a log file for errors.

---

### 4. **API Integration**

#### **REST API**

- **Description**: Expose core functionalities via a REST API for external app integration.
- **Implementation**: Use the `Flask` framework to create API endpoints for document upload, retrieval, and QA.
- **References**: [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/)

---

### 5. **Security Enhancements**

#### **Access Control**

- **Description**: Implement user authentication and role-based access to features.
- **Implementation**: Use `Flask-JWT-Extended` or similar libraries for secure authentication.

#### **Data Encryption**

- **Description**: Encrypt uploaded files and query results to enhance privacy.
- **Implementation**: Leverage Python's `cryptography` library.

---

### 6. **Enhanced Retrieval**

#### **Hybrid Scoring System**

- **Description**: Improve the retrieval system by adding Dense Passage Retrieval (DPR).
- **Implementation**: Use Hugging Face's `sentence-transformers` to generate embeddings.
- **References**: [DPR Documentation](https://github.com/facebookresearch/DPR)

#### **Semantic Clustering**

- **Description**: Implement clustering algorithms to group similar documents for better retrieval.
- **Implementation**: Use `scikit-learn`'s clustering algorithms (e.g., KMeans).

---

### 7. **Performance Optimization**

#### **Parallel Processing**

- **Description**: Use multi-threading or multiprocessing for faster file processing.
- **Implementation**: Use Python's `concurrent.futures` or `multiprocessing`.

#### **Caching System**

- **Description**: Cache embeddings or document chunks for frequently queried files.
- **Implementation**: Use `redis` or `diskcache`.

---

### 8. **Feedback System**

#### **Feedback Loop**

- **Description**: Allow users to rate responses to improve system accuracy over time.
- **Implementation**: Add a rating system in the UI and store feedback in a database.

#### **Interactive Debugging**

- **Description**: Enable users to flag incorrect answers directly from the UI.
- **Implementation**: Add a "Report Issue" button to log flagged responses.

---

### 9. **Testing and CI/CD**

#### **Automated Testing**

- **Description**: Add unit tests and integration tests to ensure robustness.
- **Implementation**: Use `pytest` for testing.

#### **Continuous Deployment**

- **Description**: Set up CI/CD pipelines for seamless updates.
- **Implementation**: Use GitHub Actions or similar services.

---

### 10. **Community Engagement**

#### **Knowledge Base**

- **Description**: Create a knowledge base or documentation portal for users and developers.
- **Implementation**: Use platforms like GitBook or ReadTheDocs.

#### **Community Contributions**

- **Description**: Open source the project and invite external contributions.
- **Implementation**: Add a `CONTRIBUTING.md` file and set up GitHub issues for community collaboration.

---

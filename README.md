# Hybrid RAG System with Memory and Tracing

This project is a cutting-edge Retrieval-Augmented Generation (RAG) system leveraging advanced techniques in natural language processing (NLP), document retrieval, and conversational memory. It uses LangChain, DeepSeek R1, and Python to provide enhanced document-based Q&A functionality.

## Features

- **Dynamic Context Awareness**: Provides accurate answers by combining BM25 and FAISS for efficient document retrieval.
- **Conversational Memory**: Remembers the flow of interactions for a more personalized experience.
- **Multiple File Support**: Upload and process multiple PDFs stored in the `data/` directory.
- **Advanced Tracing and Analytics**: Monitor queries and errors with LangSmith.
- **State-of-the-Art Tech**: Built with LangChain and the DeepSeek R1 model.

## Installation

### Prerequisites

Ensure you have Python 3.8 or higher installed.

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/hybrid-rag-system.git
   cd hybrid-rag-system
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv rag_env
   source rag_env/bin/activate  # On Windows, use `rag_env\Scripts\activate`
   ```

3. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Ollama:
   Follow the instructions at [Ollama's Official Documentation](https://ollama.com/docs) to install the Ollama CLI.

5. Pull the DeepSeek R1 model:

   ```bash
   ollama pull deepseek-r1:1.5b
   ```

6. Set up environment variables:

   - Create a `.env` file in the project root.
   - Add your LangSmith API key:
     ```env
     LANGSMITH_API_KEY=your_langsmith_api_key
     ```

7. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Upload multiple PDF files using the file uploader. The files will be stored in the `data/` directory.
2. Ask questions in the text input box, and the system will retrieve relevant information from the uploaded documents.
3. View responses and source documents directly in the Streamlit interface.

## ToDos

### Enhanced Memory Features

- **Context-Aware Memory**: Implement dynamic context retention so the system remembers the conversation's flow over multiple queries.
- **User-Specific Memory**: Allow memory to reset or persist for different users to personalize the interaction.

### File Management

- **Multiple File Formats**: Support additional file types like Word documents, CSVs, or images (via OCR for text extraction).
- **File Listing UI**: Add a sidebar that lists all uploaded files and allows users to manage (delete/view) them.

### Advanced Tracing and Analytics

- **Usage Analytics**: Track the number of queries, response times, and user feedback on responses.
- **Error Logging**: Store errors in a centralized log to troubleshoot issues more effectively.

### API Integration

- **REST API**: Expose core functionalities via a REST API using FastAPI for external integrations.

### Security Enhancements

- **Access Control**: Implement user authentication and role-based access to features using Auth0.
- **Data Encryption**: Encrypt uploaded files and query results to enhance data privacy with PyCryptodome.

### Enhanced Retrieval

- **Hybrid Scoring System**: Improve the hybrid BM25 + FAISS system by adding Dense Passage Retrieval (DPR).
- **Semantic Clustering**: Use HDBSCAN for clustering similar documents for better retrieval.

### Performance Optimization

- **Parallel Processing**: Use Ray for multi-threading to process large files faster.
- **Caching System**: Implement Redis for caching embeddings or document chunks.

### Feedback System

- **Feedback Loop**: Allow users to rate responses to improve system accuracy over time.
- **Interactive Debugging**: Let users report issues or flag incorrect answers directly from the UI.

### Testing and CI/CD

- **Automated Testing**: Add unit tests using Pytest and integration tests with LangChain's test utilities.
- **Continuous Deployment**: Use GitHub Actions for CI/CD pipelines.

### Community Engagement

- **Knowledge Base**: Create a knowledge base or documentation portal with MkDocs for users and developers.
- **Community Contributions**: Open source the project and invite external contributions.

## References

- [LangChain Documentation](https://langchain.com/)
- [Ollama Documentation](https://ollama.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangSmith](https://docs.langchain.com/docs/).

Feel free to contribute to this project and suggest new features! If you encounter any issues, please open an issue in the GitHub repository.

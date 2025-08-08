# RAG Project with Langchain and OpenAI

This project implements a Retrieval-Augmented Generation (RAG) pipeline using Langchain and OpenAI, featuring a FastAPI backend and a Streamlit frontend. It allows users to upload documents, index them, and query their contents using an LLM-powered interface.

## Features

- Upload and index documents (PDF, DOC, HTML)
- Query indexed documents using OpenAI models via a conversational interface
- Maintain chat history for sessions
- Frontend powered by Streamlit
- FastAPI backend for document and query management
- Uses ChromaDB for vector storage

## Folder Structure

```
RAG Project with Langchain and OepnAI/
├── api/                   # API utility and logic modules
├── database/              # Database and vector storage
├── frontend.py            # Streamlit app for the frontend
├── main.py                # FastAPI backend application
├── requirements.txt       # Python dependencies
└── Readme.md              # Project documentation
```

## Setup Instructions

1. **Create an `.env` file** in the project root with the following content:

    ```
    OPENAI_API_KEY="Enter your api key here"
    DB_NAME_PATH="./database/transaction.db"
    CHROMA_DB_PATH="./database/chroma_db"
    API_PORT=9001
    HOST='localhost'
    FASTAPI_URL="http://localhost:9001"
    ```

2. **Install requirements**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Backend (FastAPI) application**

    ```bash
    python main.py
    ```

4. **Run the Streamlit frontend application**

    ```bash
    streamlit run frontend.py
    ```

## Example Usage

- Upload a document via the frontend or the `/file-upload` endpoint.
- Query your documents using the chat interface.
- List or delete documents via the provided endpoints.

## Requirements

See `requirements.txt` for a full list, including:
- langchain
- fastapi
- streamlit
- chromadb
- openai
- uvicorn
- pydantic

## API Endpoints (FastAPI)

- `GET /` : Health check
- `POST /file-upload` : Upload and index a document
- `GET /list-documents` : List all uploaded documents
- `DELETE /delete-document/{file_id}` : Delete document by ID
- `POST /query` : Query indexed documents

## Notes

- Make sure your OpenAI API key is valid and has sufficient quota.
- The backend and frontend can be run independently.
- Vector and metadata storage uses local directories as configured in `.env`.

---

For more details, read through the code in `main.py` and `frontend.py`.
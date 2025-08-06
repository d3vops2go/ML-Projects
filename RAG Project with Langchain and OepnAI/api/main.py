import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv, find_dotenv
import shutil
import os
from api.utils.db_util import insert_document, delete_document_record, get_all_documents, get_chat_history, insert_application_log
from api.utils.chroma_util import index_document_to_chroma, delete_doc_from_chroma
from api.utils.langchain_util import get_rag_chain
from api.models.pydantic_models import DocumentInfo, QueryInput, QueryResponse

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

# Initialize FastAPI application
app = FastAPI()

# Test endpoint to check if the API is running
@app.get("/")
async def test_app():
    return {"message": "Welcome to the RAG Project API!"}


@app.post("/file-upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a document file.

    Args:
        file (UploadFile): The file to be uploaded.
    Allowed file types are .pdf, .docs, .html
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if file.content_type not in ["application/pdf", "application/msword", "text/html"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .pdf, .doc, and .html files are allowed.")
    
    temp_file_path = f'temp_{file.filename}'
    
    # Save File Operation
    try:
        # Save the fle to temp_file_path
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        file_id = insert_document(file.filename)
        success = index_document_to_chroma(file_id, temp_file_path)

        if success:
            return {"filename": file.filename, "message": "File uploaded successfully and saved to database.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail="Failed to index document to ChromaDB")
    finally:
        if os.path.exists(temp_file_path):
            # Delete the temporary file
            os.remove(temp_file_path)


@app.get("/list-documents", response_model=list[DocumentInfo])
async def list_documents():
    return get_all_documents()


@app.delete("/delete-document/{file_id}")
async def delete_document(file_id: int):
    """
    Endpoint to delete a document by its ID.
    
    Args:
        file_id (int): The ID of the document to be deleted.
    """
    is_delete_from_chroma = delete_doc_from_chroma(file_id)

    if is_delete_from_chroma:
        is_delete_from_db = delete_document_record(file_id)

        if is_delete_from_db:
            return {"message": f"Document with ID {file_id} deleted successfully from both database and ChromaDB."}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document from database")
        
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document from ChromaDB")


@app.post("/query", response_model=QueryResponse)
async def query(query_input: QueryInput):
    """
    Endpoint to handle queries against the indexed documents.

    Args:
        query_input (QueryInput): The input containing the question, session ID, and model name.
    """
    session_id = query_input.session_id or str(uuid.uuid4())
    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']
    
    insert_application_log(session_id, query_input.question, answer, query_input.model.value)
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


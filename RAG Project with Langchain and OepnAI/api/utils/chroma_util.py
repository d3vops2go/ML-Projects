from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv, find_dotenv
import os


# Load environment variables from .env file
_ = load_dotenv(find_dotenv()) 
openai_api_key = os.getenv("OPENAI_API_KEY")
chroma_db_path = os.getenv("CHROMA_DB_PATH")

# Chunk, Embed, and Store Documents in ChromaDB
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(embedding_function=embeddings, persist_directory=chroma_db_path or "default_chroma_db")

def load_and_split_document(file_path):
    """
    Load a document from the specified file path and split it into chunks.

    Args:
        file_path (str): The path to the document file.

    Returns:
        list: A list of Document objects containing the text chunks.
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload a .pdf, .docx, or .html file.")

    documents = loader.load()
    return text_splitter.split_documents(documents)


def index_document_to_chroma(file_id, file_path) -> bool:
    """
    Index a document to ChromaDB.

    Args:
        file_id (int): The ID of the document in the database.
        file_path (str): The path to the document file.

    Returns:
        bool: True if the document was indexed successfully, False otherwise.
    """
    try:
        documents = load_and_split_document(file_path)
        for doc in documents:
            doc.metadata = {"file_id": file_id}
        vectorstore.add_documents(documents)
        return True
    except Exception as e:
        print(f"Error indexing document {file_id}: {e}")
        return False
    

def delete_doc_from_chroma(file_id) -> bool:
    """
    Delete a document from ChromaDB.

    Args:
        file_id (int): The ID of the document to be deleted.

    Returns:
        bool: True if the document was deleted successfully, False otherwise.
    """
    try:
        # Check if file exists in ChromaDB and delete it else return False
        if not vectorstore.get(where={"file_id": file_id})['ids']:
            print(f"No document found with file_id {file_id} in ChromaDB.")
            return False
        vectorstore.delete(where={"file_id": file_id})
        return True
    except Exception as e:
        print(f"Error deleting document {file_id}: {e}")
        return False
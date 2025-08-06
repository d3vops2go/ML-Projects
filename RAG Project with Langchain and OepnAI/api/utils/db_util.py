import sqlite3
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

def get_db_connection():
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    db_name = os.getenv("DB_NAME_PATH") or "transaction.db"
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Enable row factory for dictionary-like access
    return conn


def create_tables():
    """
    Create a table in the SQLite database if it doesn't exist.
    """
    conn = get_db_connection()
    # Create table if it doesn't exist
    
    with conn:
    # Table1 - documents with columns id, filename, and timestamp
        conn.execute('''CREATE TABLE IF NOT EXISTS documents
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    # Table2 - application_logs with columns id, session_id, user_query, gpt_response, model, and created_at
        conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_query TEXT,
                     gpt_response TEXT,
                     model TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()


def insert_document(filename):
    """
    Insert a document into the documents table.

    Args:
        filename (str): The name of the document to be inserted.
    Returns:
        int: The ID of the inserted document.

    """
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documents (filename) VALUES (?)", (filename,))
        inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


def delete_document_record(file_id) -> bool:
    """
    Delete a document record from the documents table.

    Args:
        file_id (int): The ID of the document to be deleted.
    """
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (file_id,))
        # check if the deletion was successful
        if conn.total_changes == 0:
            return False
    # If we reach here, the deletion was successful
    conn.commit()
    conn.close()
    return True


def get_all_documents():
    """
    Retrieve all documents from the documents table.

    Returns:
        list: A list of dictionaries representing the documents.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]  # Convert rows to a list of dictionaries


def insert_application_log(session_id, user_query, gpt_response, model):
    """
    Insert an application log into the application_logs table.

    Args:
        session_id (str): The session ID for the log entry.
        user_query (str): The user's query.
        gpt_response (str): The response from the GPT model.
        model (str): The model used for generating the response.
    """
    conn = get_db_connection()
    with conn:
        conn.execute(
            "INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)",
            (session_id, user_query, gpt_response, model)
        )
        conn.commit()
    conn.close()


def get_chat_history(session_id):
    """
    Retrieve the chat history for a given session ID.

    Args:
        session_id (str): The session ID for which to retrieve the chat history.

    Returns:
        list: A list of dictionaries representing the chat history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_query, gpt_response FROM application_logs WHERE session_id = ?", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "assistant", "content": row['gpt_response']}
        ])
    # print(history) 
    return history


# Create tables if they do not exist
create_tables()
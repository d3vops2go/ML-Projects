import streamlit as st
import requests
import os
import uuid
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Backend API URL
API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="My Assistant", layout="centered")
st.title("💬 RAG Document Chat Assistant")

# ------------------------
# Session State Management
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ------------------------
# Sidebar for Document Upload & Management
# ------------------------
st.sidebar.header("📤 Document Management")

uploaded_file = st.sidebar.file_uploader("Upload a document (.pdf, .doc, .html)", type=["pdf", "doc", "html"])
if uploaded_file and st.sidebar.button("Upload"):
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    try:
        res = requests.post(f"{API_URL}/file-upload", files=files)
        if res.status_code == 200:
            st.sidebar.success(res.json().get("message", "File uploaded successfully"))
        else:
            st.sidebar.error(f"Error: {res.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

if st.sidebar.button("📄 Refresh Documents"):
    try:
        res = requests.get(f"{API_URL}/list-documents")
        if res.status_code == 200:
            st.session_state.docs = res.json()
        else:
            st.sidebar.error(f"Error: {res.text}")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

if "docs" in st.session_state and st.session_state.docs:
    for doc in st.session_state.docs:
        st.sidebar.write(f"ID: {doc['id']} | Name: {doc['filename']}")
        if st.sidebar.button(f"Delete {doc['id']}", key=f"del_{doc['id']}"):
            try:
                del_res = requests.delete(f"{API_URL}/delete-document/{doc['id']}")
                if del_res.status_code == 200:
                    st.sidebar.success("Deleted successfully!")
                    # Refresh docs immediately
                    res = requests.get(f"{API_URL}/list-documents")
                    if res.status_code == 200:
                        st.session_state.docs = res.json()
                else:
                    st.sidebar.error(f"Delete failed: {del_res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.sidebar.error(f"Connection error: {e}")
else:
    st.sidebar.info("No documents found. Click refresh to load.")


# ------------------------
# Chat Interface
# ------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# ------------------------
# User Input for Chat
# ------------------------
if prompt := st.chat_input("Ask me something about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send request to FastAPI backend
    payload = {
        "question": prompt,
        "session_id": st.session_state.session_id,
        "model": "gpt-4o-mini"  
    }
    try:
        res = requests.post(f"{API_URL}/query", json=payload)
        if res.status_code == 200:
            data = res.json()
            answer = data.get("answer", "No answer returned")
        else:
            answer = f"Error: {res.json().get('detail', 'Unknown error')}"
    except Exception as e:
        answer = f"Connection error: {e}"

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

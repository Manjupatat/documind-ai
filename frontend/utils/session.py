
import streamlit as st


def initialize_session():
    defaults = {
        "chat_history": [],
        "selected_document_id": None,
        "documents": [],
        "last_uploaded_file": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chat():
    st.session_state.chat_history = []


def add_message(role: str, content: str, sources=None):
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "sources": sources or []
    })

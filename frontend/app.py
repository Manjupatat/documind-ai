
import streamlit as st

from app_client import api, APIError
from components.chat_interface import render_chat_interface
from components.document_manager import render_document_manager
from utils.session import initialize_session, clear_chat


st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_session()

# Custom styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 750;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888888;
        font-size: 1rem;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.2);
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("📚 DocuMind AI")
    st.caption("Your intelligent PDF research assistant")

    st.divider()

    st.subheader("Document context")

    try:
        response = api.get_documents()
        documents = response.get("documents", [])

        document_options = {
            doc["document_id"]: (
                f"{doc.get('filename', 'Untitled')} "
                f"({doc.get('total_chunks', 0)} chunks)"
            )
            for doc in documents
        }

        selected_id = st.selectbox(
            "Chat with",
            options=[None] + list(document_options.keys()),
            format_func=lambda value: (
                "All documents"
                if value is None
                else document_options[value]
            ),
            key="document_selector"
        )

        # Clear previous conversation when changing document context.
        previous_id = st.session_state.get("previous_document_id")

        if previous_id != selected_id:
            clear_chat()
            st.session_state.previous_document_id = selected_id

        st.session_state.selected_document_id = selected_id

        st.caption(f"{len(documents)} documents available")

    except Exception as e:
        documents = []
        st.warning(f"Could not load documents: {e}")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        clear_chat()
        st.rerun()

    st.caption("Powered by FastAPI, ChromaDB and Gemini")


# ---------------- MAIN CONTENT ----------------

st.markdown(
    '<p class="main-title">DocuMind AI</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'Upload documents, discover insights and ask questions using AI.'
    '</p>',
    unsafe_allow_html=True
)

# Backend status
try:
    api.check_health()
    st.success("Backend connected", icon="🟢")
except Exception:
    st.error(
        "Backend is unavailable. Start your FastAPI server to continue.",
        icon="🔴"
    )

# Main application tabs
chat_tab, library_tab, search_tab = st.tabs([
    "💬 Chat",
    "📁 Document Library",
    "🔎 Semantic Search"
])

with chat_tab:
    render_chat_interface(
        document_id=st.session_state.selected_document_id
    )

with library_tab:
    render_document_manager()

with search_tab:
    st.subheader("Search your documents")

    search_query = st.text_input(
        "Enter a search query",
        placeholder="What are the main findings in the document?"
    )

    search_top_k = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=3
    )

    if st.button("Search documents", type="primary"):
        if len(search_query.strip()) < 3:
            st.warning("Enter at least 3 characters.")
        else:
            with st.spinner("Searching your documents..."):
                try:
                    result = api.search(
                        query=search_query,
                        document_id=st.session_state.selected_document_id,
                        top_k=search_top_k
                    )

                    st.write(
                        f"Found {result.get('total_results', 0)} results."
                    )

                    for index, item in enumerate(
                        result.get("results", []),
                        start=1
                    ):
                        with st.container(border=True):
                            st.markdown(f"**Result {index}**")
                            st.write(item.get("content", ""))

                            st.caption(
                                f"Source: {item.get('source', 'Unknown')} "
                                f"| Page: {item.get('page', 'Unknown')}"
                            )

                except APIError as e:
                    st.error(str(e))

                except Exception as e:
                    st.error(f"Search failed: {e}")

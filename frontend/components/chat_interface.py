
import streamlit as st

from app_client import api, APIError
from utils.session import add_message


def render_sources(sources):
    if not sources:
        return

    with st.expander("View answer sources"):
        for index, source in enumerate(sources, start=1):
            if isinstance(source, dict):
                filename = (
                    source.get("source")
                    or source.get("filename")
                    or source.get("file_name")
                    or "Unknown document"
                )

                page = source.get("page", source.get("page_number"))

                st.markdown(f"**{index}. {filename}**")

                if page is not None:
                    st.caption(f"Page: {page}")

                source_id = source.get("source_id")
                if source_id:
                    st.caption(f"Source ID: {source_id}")

                content = source.get("content")
                if content:
                    st.write(content)

            else:
                st.write(f"{index}. {source}")


def render_chat_interface(document_id=None):
    st.subheader("Chat with your documents")

    if document_id:
        st.caption("Asking questions about the selected document.")
    else:
        st.caption("Asking questions across all uploaded documents.")

    # Display previous messages.
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(message.get("sources", []))

    question = st.chat_input(
        "Ask something about your documents..."
    )

    if question:
        if len(question.strip()) < 3:
            st.warning("Please enter at least 3 characters.")
            return

        add_message("user", question)

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating an answer..."):
                try:
                    result = api.chat(
                        question=question,
                        document_id=document_id,
                        top_k=3
                    )

                    answer = result.get(
                        "answer",
                        "No answer was returned."
                    )

                    sources = result.get("sources", [])

                    st.markdown(answer)
                    render_sources(sources)

                    add_message(
                        "assistant",
                        answer,
                        sources
                    )

                except APIError as e:
                    error_message = f"Unable to answer your question: {e}"
                    st.error(error_message)
                    add_message("assistant", error_message)

                except Exception as e:
                    error_message = f"Backend connection failed: {e}"
                    st.error(error_message)
                    add_message("assistant", error_message)

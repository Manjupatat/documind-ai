
import streamlit as st

from app_client import api, APIError


def render_document_manager():
    st.subheader("Upload a PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_file:
        if st.button(
            "Upload and process",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Uploading and indexing your PDF..."):
                try:
                    result = api.upload_document(uploaded_file)

                    st.success(result.get("message", "Upload successful!"))

                    st.write(f"**Filename:** {result.get('filename')}")
                    st.write(f"**Chunks indexed:** {result.get('total_chunks')}")

                    st.session_state.last_uploaded_file = (
                        result.get("document_id")
                    )

                    st.rerun()

                except APIError as e:
                    st.error(str(e))

                except Exception as e:
                    st.error(f"Unable to connect to backend: {e}")

    st.divider()
    st.subheader("Your document library")

    try:
        response = api.get_documents()
        documents = response.get("documents", [])

        st.session_state.documents = documents

        st.metric("Total documents", response.get("total_documents", 0))

        if not documents:
            st.info("No documents uploaded yet.")
            return

        for document in documents:
            document_id = document["document_id"]
            filename = document.get("filename", "Untitled PDF")

            with st.container(border=True):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**📄 {filename}**")
                    st.caption(
                        f"{document.get('total_chunks', 0)} indexed chunks"
                    )

                with col2:
                    if st.button(
                        "Delete",
                        key=f"delete_{document_id}"
                    ):
                        st.session_state[f"confirm_delete_{document_id}"] = True

                if st.session_state.get(
                    f"confirm_delete_{document_id}", False
                ):
                    st.warning(f"Delete {filename}? This cannot be undone.")

                    yes_col, no_col = st.columns(2)

                    with yes_col:
                        if st.button(
                            "Confirm",
                            key=f"confirm_{document_id}"
                        ):
                            try:
                                api.delete_document(document_id)

                                if (
                                    st.session_state.selected_document_id
                                    == document_id
                                ):
                                    st.session_state.selected_document_id = None

                                st.session_state.chat_history = []
                                st.session_state.pop(
                                    f"confirm_delete_{document_id}",
                                    None
                                )

                                st.success("Document deleted.")
                                st.rerun()

                            except APIError as e:
                                st.error(str(e))

                    with no_col:
                        if st.button(
                            "Cancel",
                            key=f"cancel_{document_id}"
                        ):
                            st.session_state.pop(
                                f"confirm_delete_{document_id}",
                                None
                            )
                            st.rerun()

    except APIError as e:
        st.error(str(e))

    except Exception as e:
        st.error(f"Unable to load documents: {e}")

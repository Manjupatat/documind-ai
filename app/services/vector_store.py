
from pathlib import Path

from langchain_chroma import Chroma

from app.services.embedding_service import EmbeddingService
from collections import Counter


class VectorStore:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.persist_directory = str(
            Path("data/chroma_db").resolve()
        )

        self.collection_name = "documind_documents"

        self._vector_db = None

    @property
    def vector_db(self):

        if self._vector_db is None:

            print("Initializing ChromaDB...")

            self._vector_db = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_service.embedding_model,
                persist_directory=self.persist_directory
            )

        return self._vector_db

    def add_documents(self, documents, ids=None):

        self.vector_db.add_documents(
            documents=documents,
            ids=ids
        )

        return len(documents)

    def search(
        self,
        query: str,
        k: int = 3,
        document_id: str | None = None
    ):
        search_kwargs = {
            "query": query,
            "k": k
        }

        # Restrict retrieval to a specific uploaded document.
        if document_id:
            search_kwargs["filter"] = {
                "document_id": document_id
            }

        return self.vector_db.similarity_search(
            **search_kwargs
        )

    def get_collection_count(self):

        return self.vector_db._collection.count()

    def search_with_scores(
        self,
        query: str,
        k: int = 3,
        document_id: str | None = None
    ):
        search_kwargs = {
            "query": query,
            "k": k
        }

        if document_id:
            search_kwargs["filter"] = {
                "document_id": document_id
            }

        results = self.vector_db.similarity_search_with_score(
            **search_kwargs
        )

        return results

    def find_document_by_hash(self, file_hash: str):
        result = self.vector_db.get(
            where={"file_hash": file_hash},
            include=["metadatas"]
        )

        if not result["metadatas"]:
            return None

        metadata = result["metadatas"][0]

        return {
            "document_id": metadata.get("document_id"),
            "source": metadata.get("source")
        }

    def find_document_by_content(self, documents):
        """
        Find an existing legacy document with identical
        page-wise extracted chunk content.
        """

        incoming_chunks = Counter(
            (
                chunk.metadata.get("page"),
                chunk.page_content.strip()
            )
            for chunk in documents
        )

        result = self.vector_db.get(
            include=["documents", "metadatas"]
        )

        existing_documents = {}

        for content, metadata in zip(
            result["documents"],
            result["metadatas"]
        ):
            document_id = metadata.get("document_id")

            if not document_id:
                continue

            # Only inspect legacy documents without SHA-256.
            if metadata.get("file_hash"):
                continue

            if document_id not in existing_documents:
                existing_documents[document_id] = {
                    "source": metadata.get("source"),
                    "chunks": Counter()
                }

            existing_documents[document_id]["chunks"].update([
                (
                    metadata.get("page"),
                    content.strip()
                )
            ])

        for document_id, details in existing_documents.items():

            if details["chunks"] == incoming_chunks:
                return {
                    "document_id": document_id,
                    "source": details["source"]
                }

        return None

    def get_all_documents(self):
        result = self.vector_db.get(
            include=["metadatas"]
        )

        documents = {}

        for metadata in result["metadatas"]:
            document_id = metadata.get("document_id")

            if not document_id:
                continue

            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "filename": metadata.get("source"),
                    "total_chunks": 0
                }

            documents[document_id]["total_chunks"] += 1

        return list(documents.values())

    def delete_document(self, document_id: str):
        # Find all chunks belonging to this document.
        result = self.vector_db.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )

        document_count = len(result["ids"])

        if document_count == 0:
            return 0

        # Delete all chunks belonging to this document.
        self.vector_db._collection.delete(
            where={"document_id": document_id}
        )

        return document_count


# Shared vector store instance
vector_store = VectorStore()
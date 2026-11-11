
from pathlib import Path

from langchain_chroma import Chroma

from app.services.embedding_service import EmbeddingService


class VectorStore:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.persist_directory = str(
            Path("data/chroma_db").resolve()
        )

        self.collection_name = "documind_documents"

        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_service.embedding_model,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents, ids=None):

        self.vector_db.add_documents(
            documents=documents,
            ids=ids
        )

        return len(documents)

    # def search(self, query: str, k: int = 3):

    #     results = self.vector_db.similarity_search(
    #         query=query,
    #         k=k
    #     )

    #     return results

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

# Shared vector store instance
vector_store = VectorStore()
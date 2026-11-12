
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:

    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._embedding_model = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            print("Loading embedding model...")

            self._embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )

        return self._embedding_model

    def generate_embedding(self, text: str):
        return self.embedding_model.embed_query(text)

    def generate_embeddings(self, texts: list[str]):
        return self.embedding_model.embed_documents(texts)

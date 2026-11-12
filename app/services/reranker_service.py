
from sentence_transformers import CrossEncoder


class RerankerService:

    def __init__(self):
        self.model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self._model = None

    @property
    def model(self):
        if self._model is None:
            print("Loading reranker model...")

            self._model = CrossEncoder(
                self.model_name,
                device="cpu"
            )

        return self._model

    def rerank(
        self,
        query: str,
        documents: list,
        top_n: int = 3
    ):
        if not documents:
            return []

        pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked_results = list(zip(documents, scores))

        ranked_results.sort(
            key=lambda item: float(item[1]),
            reverse=True
        )

        return ranked_results[:top_n]


# Shared reranker instance
reranker_service = RerankerService()

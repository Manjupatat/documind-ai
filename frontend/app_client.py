
import os

import requests


API_BASE_URL = os.getenv(
    "DOCUMIND_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

API_TIMEOUT = 120


class APIError(Exception):
    """Raised when the backend API returns an error."""


class DocuMindAPI:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _handle_response(self, response):
        try:
            data = response.json()
        except ValueError:
            data = {}

        if not response.ok:
            detail = data.get("detail", response.text)

            if isinstance(detail, dict):
                detail = detail.get("message", str(detail))

            raise APIError(str(detail))

        return data

    def check_health(self):
        response = requests.get(
            f"{self.base_url}/health",
            timeout=10
        )
        return self._handle_response(response)

    def upload_document(self, uploaded_file):
        response = requests.post(
            f"{self.base_url}/api/documents/upload",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            },
            timeout=API_TIMEOUT
        )

        return self._handle_response(response)

    def get_documents(self):
        response = requests.get(
            f"{self.base_url}/api/documents/",
            timeout=30
        )

        return self._handle_response(response)

    def delete_document(self, document_id: str):
        response = requests.delete(
            f"{self.base_url}/api/documents/{document_id}",
            timeout=30
        )

        return self._handle_response(response)

    def chat(
        self,
        question: str,
        document_id: str | None = None,
        top_k: int = 3
    ):
        response = requests.post(
            f"{self.base_url}/api/documents/chat",
            json={
                "question": question,
                "document_id": document_id,
                "top_k": top_k
            },
            timeout=API_TIMEOUT
        )

        return self._handle_response(response)

    def search(
        self,
        query: str,
        document_id: str | None = None,
        top_k: int = 3
    ):
        response = requests.get(
            f"{self.base_url}/api/documents/search",
            params={
                "query": query,
                "document_id": document_id,
                "top_k": top_k
            },
            timeout=API_TIMEOUT
        )

        return self._handle_response(response)


api = DocuMindAPI()

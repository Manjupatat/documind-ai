import os
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.vector_store import vector_store
from app.services.reranker_service import reranker_service

load_dotenv()


class RAGPipeline:

    def __init__(self):

        self._llm = None

    @property
    def llm(self):

        if self._llm is None:

            api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key or api_key == "your_gemini_api_key":
                raise ValueError(
                    "Please configure GOOGLE_API_KEY in .env"
                )

            print("Initializing Gemini client...")

            self._llm = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash-lite",
                google_api_key=api_key
            )

        return self._llm

    def retrieve_documents(
        self,
        question: str,
        top_k: int = 3,
        document_id: str | None = None
    ):
        # Step 1: Retrieve more candidates from Chroma.
        candidate_documents = vector_store.search(
            query=question,
            k=max(10, top_k),
            document_id=document_id
        )

        if not candidate_documents:
            return []

        # Step 2: Rerank candidates using the cross-encoder.
        reranked_results = reranker_service.rerank(
            query=question,
            documents=candidate_documents,
            top_n=top_k
        )

        # Step 3: Return only the selected documents.
        return [
            document
            for document, score in reranked_results
        ]

    
    def build_context(self, documents):

        context_parts = []
        sources = []
        source_mapping = {}

        for doc in documents:

            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            doc_id = doc.metadata.get("document_id")

            # Identify a unique source by document and page.
            source_key = (source, page, doc_id)

            if source_key not in source_mapping:

                source_id = f"S{len(sources) + 1}"
                source_mapping[source_key] = source_id

                sources.append({
                    "source_id": source_id,
                    "source": source,
                    "page": page,
                    "document_id": doc_id
                })

            source_id = source_mapping[source_key]

            context_parts.append(
                f"""
                [{source_id}]
                Source: {source}
                Page: {page}

                Content:
                {doc.page_content}
                """
            )

        context = "\n\n".join(context_parts)

        return context, sources

    def extract_response_text(self, response):

        content = response.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):

            return "\n".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
            )

        return str(content)

    def generate_answer(
        self,
        question: str,
        context: str,
        valid_source_ids: set
    ):

        prompt = f"""
        You are DocuMind AI, an intelligent document assistant.

        Answer the user's question using ONLY the provided context.

        RULES:
        1. Never invent information.
        2. If the answer is not available in the context,
           clearly say that the document does not contain
           enough information.
        3. Cite factual claims using the source IDs provided,
           such as [S1] or [S2].
        4. Only use source IDs that appear in the context.
        5. Do not invent filenames, page numbers, or citations.
        6. Keep the answer clear and concise.
        7. If information is unavailable, do not guess.

        DOCUMENT CONTEXT:
        {context}

        USER QUESTION:
        {question}

        ANSWER:
        """

        response = self.llm.invoke(prompt)

        answer = self.extract_response_text(response)

        # Validate citations against retrieved source IDs.
        cited_ids = set(
            re.findall(r"\[S\d+\]", answer)
        )

        valid_tags = {
            f"[{source_id}]"
            for source_id in valid_source_ids
        }

        for citation in cited_ids:

            if citation not in valid_tags:
                answer = answer.replace(
                    citation,
                    "[unverified citation]"
                )

        return answer

    def ask(
        self,
        question: str,
        top_k: int = 3,
        document_id: str | None = None
    ):

        documents = self.retrieve_documents(
            question=question,
            top_k=top_k,
            document_id=document_id
        )

        if not documents:
            return {
                "question": question,
                "answer": (
                    "I couldn't find relevant information "
                    "in the uploaded documents."
                ),
                "sources": []
            }

        context, sources = self.build_context(documents)

        valid_source_ids = {
            source["source_id"]
            for source in sources
        }

        answer = self.generate_answer(
            question=question,
            context=context,
            valid_source_ids=valid_source_ids
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }


# Shared RAG pipeline instance
rag_pipeline = RAGPipeline()

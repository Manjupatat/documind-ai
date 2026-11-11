
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.vector_store import vector_store


load_dotenv()


class RAGPipeline:

    def __init__(self):

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key or api_key == "your_gemini_api_key":
            raise ValueError(
                "Please configure GOOGLE_API_KEY in .env"
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            google_api_key=api_key
        )

    def retrieve_documents(
        self,
        question: str,
        top_k: int = 3,
        document_id: str | None = None
    ):

        return vector_store.search(
            query=question,
            k=top_k,
            document_id=document_id
        )

    def build_context(self, documents):

        context_parts = []

        for doc in documents:

            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")

            context_parts.append(
                f"""
                Source: {source}
                Page: {page}

                Content:
                {doc.page_content}
                """
            )

        return "\n\n".join(context_parts)

    def generate_answer(self, question: str, context: str):

        prompt = f"""
        You are DocuMind AI, an intelligent document assistant.

        Answer the user's question using ONLY the provided context.

        Rules:
        1. Do not invent information.
        2. If the answer is not present in the context,
           clearly say that the uploaded document does not
           contain enough information to answer.
        3. Provide a clear and concise answer.
        4. Cite sources using the filename and page number.
        5. Never invent page numbers or citations.

        DOCUMENT CONTEXT:
        {context}

        USER QUESTION:
        {question}

        ANSWER:
        """

        response = self.llm.invoke(prompt)

        # Handle both string and block-based response content.
        if isinstance(response.content, str):
            return response.content

        return "\n".join(
            block["text"]
            for block in response.content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

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

        context = self.build_context(documents)

        answer = self.generate_answer(
            question=question,
            context=context
        )

        # Collect unique source references.
        sources = []
        seen = set()

        for doc in documents:

            source = doc.metadata.get("source")
            page = doc.metadata.get("page")
            doc_id = doc.metadata.get("document_id")

            source_key = (source, page, doc_id)

            if source_key not in seen:
                seen.add(source_key)

                sources.append({
                    "source": source,
                    "page": page,
                    "document_id": doc_id
                })

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }


# Shared RAG pipeline instance
rag_pipeline = RAGPipeline()


from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import rag_pipeline

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_with_documents(request: ChatRequest):

    try:
        result = rag_pipeline.ask(
            question=request.question,
            top_k=request.top_k,
            document_id=request.document_id
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        print(f"Chat processing error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process your question. Please try again."
        )

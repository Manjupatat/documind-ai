
from fastapi import APIRouter, HTTPException, Query

from app.services.vector_store import vector_store

router = APIRouter()


@router.get("/search")
def search_documents(
    query: str = Query(..., min_length=3),
    top_k: int = Query(default=3, ge=1, le=10),
    document_id: str | None = Query(default=None)
):

    try:
        results = vector_store.search(
            query=query,
            k=top_k,
            document_id=document_id
        )

        return {
            "query": query,
            "document_id": document_id,
            "total_results": len(results),
            "results": [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "document_id": doc.metadata.get("document_id")
                }
                for doc in results
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

from fastapi import APIRouter

from app.services.vector_store import vector_store
from fastapi import APIRouter, HTTPException
router = APIRouter()


@router.get("/")
def list_documents():
    documents = vector_store.get_all_documents()

    return {
        "total_documents": len(documents),
        "documents": documents
    }


@router.delete("/{document_id}")
def delete_document(document_id: str):

    deleted_count = vector_store.delete_document(document_id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "deleted_chunks": deleted_count
    }



import hashlib
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_processor import DocumentProcessor
from app.services.vector_store import vector_store

router = APIRouter()

processor = DocumentProcessor()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Step 1: Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:
        # Step 2: Read uploaded file
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Step 3: Validate file size (10 MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File size must be below 10 MB."
            )

        # Step 4: Generate SHA-256 hash
        file_hash = hashlib.sha256(content).hexdigest()

        # Step 5: Check for duplicate document
        existing_document = vector_store.find_document_by_hash(
            file_hash
        )

        if existing_document:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "This document has already been uploaded.",
                    "existing_document_id": existing_document["document_id"],
                    "filename": existing_document["source"]
                }
            )

        

        # Step 6: Process PDF
        chunks = processor.process_pdf(
            content,
            file.filename
        )

        # Check for duplicates among legacy documents without SHA-256 metadata.
        existing_document = vector_store.find_document_by_content(
            chunks
        )

        if existing_document:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "This document has already been uploaded (matching extracted content).",
                    "existing_document_id": existing_document["document_id"],
                    "filename": existing_document["source"]
                }
            )
        # Step 7: Generate document ID
        document_id = str(uuid4())

        # Step 8: Add metadata to every chunk
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
            chunk.metadata["file_hash"] = file_hash

        # Step 9: Generate unique chunk IDs
        chunk_ids = [
            f"{document_id}_{i}"
            for i in range(len(chunks))
        ]

        # Step 10: Store chunks and embeddings
        stored_count = vector_store.add_documents(
            chunks,
            ids=chunk_ids
        )

        return {
            "message": "Document uploaded and indexed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "total_chunks": stored_count,
            "vector_database_count": vector_store.get_collection_count()
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:
        await file.close()

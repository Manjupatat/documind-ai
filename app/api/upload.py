
# from fastapi import APIRouter, UploadFile, File, HTTPException

# from app.services.document_processor import DocumentProcessor

# router = APIRouter()

# processor = DocumentProcessor()

# @router.post("/upload")
# async def upload_document(file: UploadFile = File(...)):

#     # Validate file type
#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(
#             status_code=400,
#             detail="Only PDF files are supported."
#         )

#     # Read file
#     content = await file.read()

#     # Validate file size (10 MB)
#     if len(content) > 10 * 1024 * 1024:
#         raise HTTPException(
#             status_code=413,
#             detail="File size must be below 10 MB."
#         )

#     if not content:
#         raise HTTPException(
#             status_code=400,
#             detail="Uploaded file is empty."
#         )

#     try:
#         chunks = processor.process_pdf(
#             content,
#             file.filename
#         )

#         return {
#             "filename": file.filename,
#             "total_chunks": len(chunks),
#             "chunks": [
#                 {
#                     "content": chunk.page_content,
#                     "metadata": chunk.metadata
#                 }
#                 for chunk in chunks
#             ]
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=str(e)
#         )

#     finally:
#         await file.close()



from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_processor import DocumentProcessor
# from app.services.vector_store import VectorStore
from app.services.vector_store import vector_store

router = APIRouter()

processor = DocumentProcessor()
# vector_store = vector_store()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size must be below 10 MB."
        )

    try:
        # Step 1: Process PDF
        chunks = processor.process_pdf(
            content,
            file.filename
        )

        # Step 2: Create unique document ID
        document_id = str(uuid4())

        # Step 3: Add document metadata
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id

        # Step 4: Generate unique IDs for chunks
        chunk_ids = [
            f"{document_id}_{i}"
            for i in range(len(chunks))
        ]

        # Step 5: Store documents and embeddings
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

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:
        await file.close()

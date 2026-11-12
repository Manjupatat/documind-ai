from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router

app = FastAPI(
    title="DocuMind AI",
    description="AI-powered document question answering system",
    version="1.0.0"
)

app.include_router(
    upload_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    search_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    chat_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    documents_router,
    prefix="/api/documents",
    tags=["Documents"]
)

@app.get("/")
def home():
    return {"message": "Welcome to DocuMind AI"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
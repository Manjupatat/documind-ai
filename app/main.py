# from fastapi import FastAPI

# from app.api.upload import router as upload_router
# from app.api.search import router as search_router
# from app.api.chat import router as chat_router
# from app.api.documents import router as documents_router

# app = FastAPI(
#     title="DocuMind AI",
#     description="AI-powered document question answering system",
#     version="1.0.0"
# )

# app.include_router(
#     upload_router,
#     prefix="/api/documents",
#     tags=["Documents"]
# )

# app.include_router(
#     search_router,
#     prefix="/api/documents",
#     tags=["Documents"]
# )

# app.include_router(
#     chat_router,
#     prefix="/api/documents",
#     tags=["Documents"]
# )

# app.include_router(
#     documents_router,
#     prefix="/api/documents",
#     tags=["Documents"]
# )

# @app.get("/")
# def home():
#     return {"message": "Welcome to DocuMind AI"}


# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}



from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import upload, search, chat, documents

app = FastAPI(
    title="DocuMind AI",
    description="AI-powered PDF assistant using RAG",
    version="1.0.0",
)

# Existing API routes
app.include_router(upload.router, prefix="/api/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/documents", tags=["Documents"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])

# Frontend directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Serve CSS and JavaScript
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
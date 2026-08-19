import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers.trace import router as trace_router
from app.routers.chat import router as chat_router
from app.routers.snippets import router as snippets_router

load_dotenv()

app = FastAPI(title="CodeTrace API", version="0.1.0")
configured_origin = os.environ.get("CODETRACE_ALLOWED_ORIGIN")
allowed_origins = [origin.strip() for origin in configured_origin.split(",")] if configured_origin else ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(trace_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(snippets_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

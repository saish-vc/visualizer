from fastapi import APIRouter, HTTPException

from app.schemas.snippet import SnippetCreate, SnippetResponse, SnippetTraceResponse
from app.services.snippet_store import create_snippet, get_snippet
from app.services.trace_service import trace_cpp

router = APIRouter(prefix="/snippets", tags=["snippets"])


@router.post("", response_model=SnippetResponse, status_code=201)
def save_snippet(request: SnippetCreate) -> SnippetResponse:
    return SnippetResponse(**create_snippet(request.code))


@router.get("/{snippet_id}", response_model=SnippetTraceResponse)
def load_snippet(snippet_id: str) -> SnippetTraceResponse:
    snippet = get_snippet(snippet_id)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return SnippetTraceResponse(**snippet, trace=trace_cpp(snippet["code"]).model_dump())


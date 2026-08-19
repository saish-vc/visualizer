from fastapi import APIRouter

from app.schemas.trace import TraceRequest, TraceResponse
from app.services.trace_service import trace_cpp

router = APIRouter(tags=["trace"])


@router.post("/trace", response_model=TraceResponse)
def create_trace(request: TraceRequest) -> TraceResponse:
    return trace_cpp(request.code)


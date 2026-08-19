from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.nim_client import stream_chat

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    def events():
        for token in stream_chat(request):
            yield f"data: {token.replace(chr(10), chr(92) + 'n')}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


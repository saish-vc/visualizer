from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    code: str = Field(max_length=100_000)
    current_line: int | None = None
    locals: dict[str, str] = Field(default_factory=dict)
    call_stack: list[str] = Field(default_factory=list)
    message: str = Field(min_length=1, max_length=10_000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


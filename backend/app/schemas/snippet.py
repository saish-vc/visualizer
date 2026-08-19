from datetime import datetime

from pydantic import BaseModel, Field


class SnippetCreate(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)


class SnippetResponse(BaseModel):
    id: str
    code: str
    created_at: datetime


class SnippetTraceResponse(SnippetResponse):
    trace: dict


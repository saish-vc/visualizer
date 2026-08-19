from pydantic import BaseModel, Field


class TraceRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)


class TraceStep(BaseModel):
    step: int
    line: int
    function: str
    locals: dict[str, str]
    call_stack: list[str]
    stdout_delta: str = ""


class TraceResponse(BaseModel):
    success: bool
    compile_error: str | None = None
    steps: list[TraceStep] = Field(default_factory=list)
    final_stdout: str = ""
    truncated: bool = False
    truncation_reason: str | None = None


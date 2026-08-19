from __future__ import annotations

import tempfile
import subprocess
from pathlib import Path

from app.schemas.trace import TraceResponse
from app.services.compiler import compile_cpp
from app.services.gdb_tracer import TraceLimit, trace_binary
from app.services.runner import run_program


def trace_cpp(code: str) -> TraceResponse:
    with tempfile.TemporaryDirectory(prefix="codetrace-") as directory:
        root = Path(directory)
        source = root / "prog.cpp"
        binary = root / "prog"
        source.write_text(code, encoding="utf-8")
        try:
            compiled, stderr = compile_cpp(source, binary)
        except subprocess.TimeoutExpired:
            return TraceResponse(success=False, compile_error="Compilation timed out.")
        if not compiled:
            return TraceResponse(success=False, compile_error=stderr)
        stdout, timed_out = run_program(binary, source.with_suffix(".final_stdout"))
        try:
            steps = trace_binary(binary, source)
        except TraceLimit as limit:
            return TraceResponse(success=True, steps=limit.steps, truncated=True, truncation_reason="Maximum step count or execution time exceeded")
        except Exception as error:
            return TraceResponse(success=False, compile_error=f"Execution failed: {error}")
        stdout_file = source.with_suffix(".stdout")
        final_stdout = stdout_file.read_text(encoding="utf-8") if stdout_file.exists() else ""
        return TraceResponse(success=True, steps=steps, final_stdout=stdout, truncated=timed_out,
                             truncation_reason="Program timed out" if timed_out else None)

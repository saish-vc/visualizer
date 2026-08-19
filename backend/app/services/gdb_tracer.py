from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from pygdbmi.gdbcontroller import GdbController

from app.schemas.trace import TraceStep


SKIPPED_FILE_GLOBS = ("/usr/include/*", "/usr/lib/*", "/usr/src/*")


class TraceLimit(Exception):
    def __init__(self, steps: list[TraceStep]) -> None:
        self.steps = steps


def _result(records: list[dict], cls: str, key: str) -> str:
    for record in records:
        if record.get("type") == "result" and record.get("message") == cls:
            return str(record.get("payload", {}).get(key, ""))
    return ""


def _exited(records: list[dict]) -> bool:
    for record in records:
        payload = record.get("payload") or {}
        if record.get("type") == "notify" and record.get("message") == "stopped" and str(payload.get("reason", "")).startswith("exited"):
            return True
        if record.get("type") == "notify" and record.get("message") == "thread-group-exited":
            return True
        if record.get("type") == "result" and record.get("message") == "error" and "not being run" in str(payload.get("msg", "")):
            return True
    return False


def _frame(records: list[dict]) -> tuple[int, str, str]:
    for record in records:
        payload = record.get("payload", {})
        if record.get("type") == "notify" and record.get("message") == "stopped":
            frame = payload.get("frame", {})
            return int(frame.get("line", 0)), str(frame.get("func", "?")), str(frame.get("fullname", frame.get("file", "")))
    return 0, "?", ""


def trace_binary(binary: Path, source: Path, max_steps: int = 2000, max_seconds: float = 5.0) -> list[TraceStep]:
    controller = GdbController(command=["gdb", "--interpreter=mi2", "--quiet"])
    steps: list[TraceStep] = []
    try:
        def send(command: str) -> list[dict]:
            return controller.write(command, timeout_sec=5, raise_error_on_timeout=True)

        send(f"file {binary.as_posix()}")
        for pattern in SKIPPED_FILE_GLOBS:
            send(f"skip -gfi {pattern}")
        send("break main")
        output_path = source.with_suffix(".stdout")
        if output_path.exists():
            output_path.unlink()
        current_records = send(f"run > {output_path.as_posix()}")
        stdout_before = ""
        started = time.monotonic()
        for index in range(max_steps):
            if time.monotonic() - started > max_seconds:
                raise TraceLimit(steps)
            if _exited(current_records):
                break
            line, function, file = _frame(current_records)
            if file and not file.endswith(source.name):
                current_records = send("-exec-finish")
                continue
            records = send("-stack-list-frames")
            locals_records = send("-stack-list-variables --all-values")
            locals_map: dict[str, str] = {}
            for record in locals_records:
                if record.get("type") == "result" and record.get("message") == "done":
                    for item in record.get("payload", {}).get("variables", []):
                        locals_map[str(item.get("name"))] = str(item.get("value", ""))
            stack_records = records
            stack: list[str] = []
            for record in stack_records:
                if record.get("type") == "result" and record.get("message") == "done":
                    stack = [str(frame.get("func", "?")) for frame in record.get("payload", {}).get("stack", [])]
            output_path = source.with_suffix(".stdout")
            current_stdout = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            delta = current_stdout[len(stdout_before):]
            stdout_before = current_stdout
            if line:
                steps.append(TraceStep(step=len(steps), line=line, function=function, locals=locals_map, call_stack=stack, stdout_delta=delta))
            current_records = send("-exec-step")
        else:
            raise TraceLimit(steps)
        final_path = source.with_suffix(".stdout")
        remaining = final_path.read_text(encoding="utf-8")[len(stdout_before):] if final_path.exists() else ""
        if remaining and steps:
            steps[-1] = steps[-1].model_copy(update={"stdout_delta": steps[-1].stdout_delta + remaining})
        return steps
    finally:
        try:
            controller.write("-gdb-exit", timeout_sec=1, raise_error_on_timeout=False)
        finally:
            controller.gdb_process.kill()

from __future__ import annotations

import json
import os
from collections.abc import Iterator

import httpx

from app.schemas.chat import ChatRequest


def _system_prompt(request: ChatRequest) -> str:
    state = json.dumps({"line": request.current_line, "locals": request.locals, "call_stack": request.call_stack}, indent=2)
    return f"""You are CodeTrace, a patient C++ execution tutor. Explain the user's code using the exact execution state supplied below. Never invent variable values. Mention source line numbers when relevant. If the state is insufficient, say what is missing.

SOURCE CODE:
```cpp
{request.code}
```

CURRENT EXECUTION STATE:
```json
{state}
```"""


def stream_chat(request: ChatRequest) -> Iterator[str]:
    api_key = os.environ.get("NIM_API_KEY")
    endpoint = os.environ.get("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    model = os.environ.get("NIM_MODEL", "meta/llama-3.1-8b-instruct")
    if not api_key:
        yield "NIM_API_KEY is not configured on the backend."
        return
    messages = [{"role": "system", "content": _system_prompt(request)}]
    messages.extend(message.model_dump() for message in request.history)
    messages.append({"role": "user", "content": request.message})
    try:
        with httpx.stream("POST", f"{endpoint.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json={"model": model, "messages": messages, "temperature": 0.2, "stream": True}, timeout=60.0) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data).get("choices", [{}])[0].get("delta", {}).get("content")
                except json.JSONDecodeError:
                    continue
                if delta:
                    yield delta
    except httpx.HTTPError as error:
        yield f"NIM request failed: {error}"


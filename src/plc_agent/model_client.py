"""Minimal OpenAI-compatible chat client for DMXAPI."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://www.dmxapi.cn/v1"


@dataclass(frozen=True)
class ChatCompletion:
    content: str
    model: str | None
    usage: dict[str, Any]
    raw_response: dict[str, Any]


class ModelApiError(RuntimeError):
    """The model endpoint rejected or returned an invalid response."""


def _decode_body(body: bytes) -> str:
    for encoding in ("utf-8", "gb18030"):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def chat_completion(
    *,
    model: str,
    messages: list[dict[str, str]],
    api_key: str | None = None,
    base_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> ChatCompletion:
    if not model.strip():
        raise ValueError("model must not be empty")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    resolved_key = api_key or os.environ.get("DMXAPI_API_KEY")
    if not resolved_key:
        raise ValueError("DMXAPI_API_KEY is not set")

    resolved_base_url = (
        base_url or os.environ.get("DMXAPI_BASE_URL") or DEFAULT_BASE_URL
    ).rstrip("/")
    body = json.dumps(
        {"model": model, "messages": messages, "stream": False},
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        f"{resolved_base_url}/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {resolved_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_text = _decode_body(response.read())
    except HTTPError as exc:
        error_body = _decode_body(exc.read())
        raise ModelApiError(f"DMXAPI HTTP {exc.code}: {error_body}") from exc
    except TimeoutError as exc:
        raise ModelApiError(
            f"DMXAPI request timed out after {timeout_seconds} seconds"
        ) from exc
    except URLError as exc:
        raise ModelApiError(f"DMXAPI request failed: {exc.reason}") from exc

    try:
        payload: Any = json.loads(response_text)
        content = payload["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise ModelApiError("DMXAPI returned an invalid chat response") from exc

    if not isinstance(payload, dict) or not isinstance(content, str):
        raise ModelApiError("DMXAPI returned an invalid chat response")

    usage = payload.get("usage")
    return ChatCompletion(
        content=content,
        model=payload.get("model"),
        usage=usage if isinstance(usage, dict) else {},
        raw_response=payload,
    )

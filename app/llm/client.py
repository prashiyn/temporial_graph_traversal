from __future__ import annotations

import httpx

from app.config import get_settings
from app.llm.config import get_use_case_config


def completion_via_doc_processing(use_case: str, messages: list[dict]) -> str | None:
    settings = get_settings()
    base_url = settings.doc_processing_base_url
    if not base_url:
        return None

    use_case_config = get_use_case_config(use_case)
    provider = use_case_config.get("provider", "openai")
    model = use_case_config.get("model")
    reasoning_effort = use_case_config.get("reasoning_effort")
    response_format = use_case_config.get("response_format")
    timeout_seconds = int(use_case_config.get("timeout_seconds", settings.doc_processing_timeout_seconds))

    payload: dict = {
        "provider": provider,
        "messages": messages,
    }
    if model:
        payload["model"] = model
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    if response_format:
        payload["response_format"] = response_format

    endpoint = f"{base_url.rstrip('/')}/llm/complete"
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("content")
    except Exception:  # noqa: BLE001
        return None

import json
import os

import httpx
import pytest

from openai_sdk_compat_tester.test_support import conversation_messages


def _assert_reasoning_effort_echoes_upstream(model_name: str, effort: str) -> None:
    base_url = os.getenv("OPENAI_COMPAT_BASE_URL", "http://127.0.0.1:18080/v1").rstrip(
        "/"
    )
    api_key = os.getenv("OPENAI_COMPAT_API_KEY", "compat-test")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model_name,
        "store": False,
        "stream": True,
        "instructions": "Compute 1 + 1. Answer with just the number.",
        "reasoning": {"effort": effort},
        "input": [{"role": "user", "content": "Compute 1 + 1."}],
    }

    created_effort = None
    completed_effort = None
    with httpx.Client(timeout=30.0, trust_env=True, headers=headers) as client:
        with client.stream("POST", f"{base_url}/responses", json=payload) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines():
                if raw_line is None:
                    continue
                line = (
                    raw_line
                    if isinstance(raw_line, str)
                    else raw_line.decode("utf-8", "replace")
                )
                if not line.startswith("data: "):
                    continue
                try:
                    event = json.loads(line[6:])
                except Exception:
                    continue

                response_payload = event.get("response") or {}
                reasoning = response_payload.get("reasoning") or {}
                if event.get("type") == "response.created":
                    created_effort = reasoning.get("effort")
                elif event.get("type") == "response.completed":
                    completed_effort = reasoning.get("effort")
                    break

    assert created_effort == effort
    assert completed_effort == effort


def test_chat_reasoning_effort(live_client, model_name, turn_mode):
    try:
        response = live_client.chat.completions.create(
            model=model_name,
            messages=conversation_messages(
                [{"role": "user", "content": "Compute 1 + 1."}], turn_mode
            ),
            reasoning_effort="medium",
            max_tokens=50,
        )
    except Exception as exc:
        pytest.skip(f"reasoning_effort not supported for this endpoint/model: {exc}")

    assert response.choices[0].message.content
    _assert_reasoning_effort_echoes_upstream(model_name, "medium")

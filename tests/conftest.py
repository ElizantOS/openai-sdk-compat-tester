import os
import urllib.error
import urllib.request
import warnings

import httpx
import pytest
from openai import OpenAI

from openai_sdk_compat_tester.live_config import choose_model_id, extract_model_ids


def _env_flag(name: str) -> bool:
    value = os.getenv(name, "")
    return value.lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session")
def live_client() -> OpenAI:
    if not _env_flag("OPENAI_COMPAT_RUN_LIVE"):
        pytest.skip("set OPENAI_COMPAT_RUN_LIVE=1 to run live compatibility tests")

    base_url = os.getenv("OPENAI_COMPAT_BASE_URL", "http://127.0.0.1:18080/v1").rstrip(
        "/"
    )
    api_key = os.getenv("OPENAI_COMPAT_API_KEY", "compat-test")
    if base_url.endswith("/compat/v1"):
        readyz_url = base_url.removesuffix("/compat/v1") + "/readyz"
    else:
        readyz_url = base_url.removesuffix("/v1") + "/readyz"

    try:
        with urllib.request.urlopen(readyz_url, timeout=5) as response:
            if response.status != 200:
                pytest.skip(
                    f"router is not ready: GET {readyz_url} -> {response.status}"
                )
    except (urllib.error.URLError, TimeoutError) as exc:
        pytest.skip(f"router is not reachable at {readyz_url}: {exc}")

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=httpx.Client(trust_env=True),
    )


@pytest.fixture(scope="session")
def model_name(live_client) -> str:
    configured_model = os.getenv("OPENAI_COMPAT_MODEL", "").strip()
    try:
        response = live_client.models.list()
    except Exception as exc:
        pytest.skip(f"/v1/models is required before chat live tests can run: {exc}")

    try:
        available_models = extract_model_ids(response)
        selected_model, used_fallback = choose_model_id(
            available_models, configured_model
        )
    except ValueError as exc:
        pytest.skip(str(exc))

    if used_fallback:
        warnings.warn(
            (
                f"OPENAI_COMPAT_MODEL={configured_model!r} is not advertised by /v1/models; "
                f"falling back to {selected_model!r}"
            ),
            stacklevel=1,
        )
    return selected_model


@pytest.fixture(params=["single-turn", "multi-turn"], ids=["single-turn", "multi-turn"])
def turn_mode(request) -> str:
    return request.param


@pytest.fixture(scope="session")
def tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo back the provided text.",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]


@pytest.fixture(scope="session")
def tools_multi(tools):
    return tools + [
        {
            "type": "function",
            "function": {
                "name": "other_tool",
                "description": "Another tool.",
                "parameters": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]

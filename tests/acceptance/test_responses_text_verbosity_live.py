import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
    responses_function_call_items,
)


def test_responses_text_verbosity_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        text={"verbosity": "high"},
    )

    assert_completed_response(response)
    assert response.text.verbosity == "high"

import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
    responses_function_call_items,
)


def test_responses_parallel_tool_calls_false_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        parallel_tool_calls=False,
    )

    assert_completed_response(response)
    assert response.parallel_tool_calls is False

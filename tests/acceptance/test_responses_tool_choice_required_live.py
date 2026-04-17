import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
    responses_function_call_items,
)


def test_responses_tool_choice_required_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        instructions="Use the provided tool. Do not answer directly.",
        input=[{"role": "user", "content": "What is the weather in SF?"}],
        tools=[RESPONSES_WEATHER_TOOL],
        tool_choice={"type": "function", "name": "get_weather"},
    )

    assert_completed_response(response)
    items = responses_function_call_items(response)
    assert items
    assert items[0].name == "get_weather"

import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
)


def test_responses_previous_response_id_streamed_function_call_output_live(live_client, model_name: str):
    response_id = None
    function_call = None
    with live_client.responses.stream(
        model=model_name,
        instructions="Use the provided tool. Do not answer directly.",
        input=[{"role": "user", "content": "What is the weather in SF?"}],
        tools=[RESPONSES_WEATHER_TOOL],
        tool_choice={"type": "function", "name": "get_weather"},
    ) as stream:
        for event in stream:
            if event.type == "response.output_item.done" and getattr(event.item, "type", "") == "function_call":
                function_call = event.item
            if event.type == "response.completed":
                response_id = event.response.id

    assert response_id
    assert function_call is not None

    second = live_client.responses.create(
        model=model_name,
        previous_response_id=response_id,
        input=[{"type": "function_call_output", "call_id": function_call.call_id, "output": '{"weather":"sunny"}'}],
        instructions="Answer in one short sentence.",
    )

    assert_completed_response(second)
    assert second.output

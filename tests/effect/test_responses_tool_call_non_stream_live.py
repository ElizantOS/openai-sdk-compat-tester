from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    parse_response_function_arguments,
    response_conversation_input,
    responses_function_call_items,
)


def test_responses_tool_call_non_stream_live(live_client, model_name: str, turn_mode: str):
    response = live_client.responses.create(
        model=model_name,
        instructions="Use the provided tool. Do not answer directly.",
        input=response_conversation_input({"role": "user", "content": "What's the weather like in San Francisco?"}, turn_mode),
        tools=[RESPONSES_WEATHER_TOOL],
    )

    assert_completed_response(response)
    items = responses_function_call_items(response)
    assert items
    first = items[0]
    assert first.name == "get_weather"
    assert first.call_id
    assert parse_response_function_arguments(first)["location"]

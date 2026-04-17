from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    collect_response_stream_events,
    first_event_with_prefix,
    parse_response_function_arguments,
    response_conversation_input,
    responses_function_call_items,
)


def test_responses_tool_call_stream_live(live_client, model_name: str, turn_mode: str):
    event_types, response = collect_response_stream_events(
        live_client.responses.stream(
            model=model_name,
            instructions="Use the provided tool. Do not answer directly.",
            input=response_conversation_input({"role": "user", "content": "What's the weather like in San Francisco?"}, turn_mode),
            tools=[RESPONSES_WEATHER_TOOL],
        )
    )

    assert_completed_response(response)
    assert first_event_with_prefix(event_types, "response.function_call_arguments") is not None
    assert "response.output_item.done" in event_types
    assert "response.completed" in event_types

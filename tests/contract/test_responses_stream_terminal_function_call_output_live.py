from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    parse_response_function_arguments,
    responses_function_call_items,
)


def test_responses_stream_terminal_function_call_output_live(live_client, model_name: str):
    done_call = None
    terminal_response = None

    with live_client.responses.stream(
        model=model_name,
        instructions="Use the provided tool. Do not answer directly.",
        input=[{"role": "user", "content": "What is the weather in San Francisco?"}],
        tools=[RESPONSES_WEATHER_TOOL],
        tool_choice={"type": "function", "name": "get_weather"},
    ) as stream:
        for event in stream:
            if event.type == "response.output_item.done" and getattr(event.item, "type", "") == "function_call":
                done_call = event.item
            elif event.type == "response.completed":
                terminal_response = event.response
        final_response = stream.get_final_response()

    assert done_call is not None
    assert terminal_response is not None
    assert_completed_response(terminal_response)

    terminal_calls = responses_function_call_items(terminal_response)
    assert terminal_calls, "response.completed.response.output must include the completed function_call item"
    terminal_call = terminal_calls[0]
    assert terminal_call.name == "get_weather"
    assert terminal_call.call_id == done_call.call_id
    assert parse_response_function_arguments(terminal_call)["location"]

    final_calls = responses_function_call_items(final_response)
    assert final_calls
    assert final_calls[0].call_id == done_call.call_id

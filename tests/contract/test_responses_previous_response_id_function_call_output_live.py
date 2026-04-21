from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
)


def test_responses_previous_response_id_function_call_output_live(live_client, model_name: str):
    first = live_client.responses.create(
        model=model_name,
        instructions="Use the provided tool. Do not answer directly.",
        input=[{"role": "user", "content": "What is the weather in SF?"}],
        tools=[RESPONSES_WEATHER_TOOL],
        tool_choice={"type": "function", "name": "get_weather"},
    )
    function_call = next(item for item in first.output if item.type == "function_call")

    second = live_client.responses.create(
        model=model_name,
        previous_response_id=first.id,
        input=[{"type": "function_call_output", "call_id": function_call.call_id, "output": '{"weather":"sunny"}'}],
        instructions="Answer in one short sentence.",
    )

    assert_completed_response(second)
    assert second.output

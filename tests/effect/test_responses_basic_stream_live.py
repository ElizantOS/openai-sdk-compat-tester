from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    collect_response_stream_events,
    response_conversation_input,
)


def test_responses_basic_stream_live(live_client, model_name: str, turn_mode: str):
    event_types, response = collect_response_stream_events(
        live_client.responses.stream(
            model=model_name,
            input=response_conversation_input(
                {"role": "user", "content": "Count from 1 to 5."},
                turn_mode,
            ),
        )
    )

    assert_completed_response(response)
    assert event_types
    assert "response.completed" in event_types

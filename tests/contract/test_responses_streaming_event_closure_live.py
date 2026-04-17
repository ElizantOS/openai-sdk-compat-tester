from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    collect_response_stream_events,
    first_event_with_prefix,
    responses_output_types,
    responses_text,
)


def test_responses_streaming_event_closure_live(live_client, model_name: str):
    event_types, response = collect_response_stream_events(
        live_client.responses.stream(
            model=model_name,
            input=[{"role": "user", "content": "Count from 1 to 5."}],
        )
    )

    assert_completed_response(response)
    assert "response.created" in event_types
    assert "response.completed" in event_types
    assert first_event_with_prefix(event_types, "response.output_text") is not None

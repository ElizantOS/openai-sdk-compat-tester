from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    collect_response_stream_events,
    response_conversation_input,
    responses_output_types,
    responses_text,
)


def test_responses_non_stream_aggregation_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Reply with exactly: ok"}],
    )

    assert_completed_response(response)
    assert response.output
    assert "message" in responses_output_types(response)
    assert getattr(response.usage, "input_tokens", 0) > 0
    assert getattr(response.usage, "output_tokens", 0) > 0

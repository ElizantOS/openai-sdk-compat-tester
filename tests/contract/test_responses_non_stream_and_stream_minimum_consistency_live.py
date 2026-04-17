from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    collect_response_stream_events,
    first_event_with_prefix,
    responses_output_types,
    responses_text,
)


def test_responses_non_stream_and_stream_minimum_consistency_live(live_client, model_name: str):
    prompt = [{"role": "user", "content": "Reply with exactly: ok"}]
    non_stream = live_client.responses.create(model=model_name, input=prompt)
    _, stream_response = collect_response_stream_events(live_client.responses.stream(model=model_name, input=prompt))

    assert_completed_response(non_stream)
    assert_completed_response(stream_response)
    assert non_stream.model == stream_response.model
    assert non_stream.store == stream_response.store
    assert responses_output_types(non_stream)
    assert stream_response.id
    assert responses_text(non_stream)

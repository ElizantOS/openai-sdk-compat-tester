from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
)


def test_responses_streaming_partial_consumption_live(live_client, model_name: str):
    with live_client.responses.stream(
        model=model_name,
        input=[{"role": "user", "content": "Count from 1 to 5."}],
    ) as stream:
        iterator = iter(stream)
        first = next(iterator)
        second = next(iterator)
        remaining = [event.type for event in iterator]
        response = stream.get_final_response()

    assert first.type
    assert second.type
    assert remaining
    assert_completed_response(response)

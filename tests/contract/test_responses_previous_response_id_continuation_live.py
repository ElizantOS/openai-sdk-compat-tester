from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
)


def test_responses_previous_response_id_continuation_live(live_client, model_name: str):
    first = live_client.responses.create(model=model_name, input=[{"role": "user", "content": "My name is Alice."}])
    second = live_client.responses.create(
        model=model_name,
        previous_response_id=first.id,
        input=[{"role": "user", "content": "Say hello."}],
    )

    assert_completed_response(second)
    assert second.prompt_cache_key
    assert second.prompt_cache_key != first.prompt_cache_key

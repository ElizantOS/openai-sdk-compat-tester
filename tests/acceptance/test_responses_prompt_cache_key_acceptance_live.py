from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
)


def test_responses_prompt_cache_key_acceptance_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        prompt_cache_key="sdk-live-prompt-cache",
    )

    assert_completed_response(response)
    assert response.prompt_cache_key

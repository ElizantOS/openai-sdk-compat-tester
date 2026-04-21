from openai_sdk_compat_tester.test_support import assert_completed_response


def test_responses_default_instructions_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello in exactly 3 words."}],
    )

    assert_completed_response(response)
    assert response.instructions == "You are a helpful assistant."

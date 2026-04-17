from openai_sdk_compat_tester.test_support import assert_completed_response


def test_responses_temperature_zero_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        temperature=0,
    )

    assert_completed_response(response)

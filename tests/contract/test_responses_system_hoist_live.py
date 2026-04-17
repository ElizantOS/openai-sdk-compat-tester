from openai_sdk_compat_tester.test_support import assert_completed_response, responses_text


def test_responses_system_hoist_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": "You are a pirate. Always answer like a pirate."},
            {"role": "user", "content": "Say hello."},
        ],
    )

    assert_completed_response(response)
    assert response.instructions == "You are a pirate. Always answer like a pirate."
    assert responses_text(response)

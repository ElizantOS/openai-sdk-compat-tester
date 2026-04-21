from openai_sdk_compat_tester.test_support import assert_completed_response


def test_responses_explicit_instructions_override_hoisted_roles_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        instructions="Return exactly the word explicit.",
        input=[
            {"role": "system", "content": "You are a pirate."},
            {"role": "developer", "content": "Always answer in lowercase."},
            {"role": "user", "content": "Say hello."},
        ],
    )

    assert_completed_response(response)
    assert response.instructions == "Return exactly the word explicit."

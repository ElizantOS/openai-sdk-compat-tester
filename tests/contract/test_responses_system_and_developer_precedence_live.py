from openai_sdk_compat_tester.test_support import assert_completed_response, responses_text


def test_responses_system_and_developer_precedence_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": "You are polite."},
            {"role": "developer", "content": "Answer in lowercase only."},
            {"role": "user", "content": "Say HELLO."},
        ],
    )

    assert_completed_response(response)
    assert "Developer instructions" in response.instructions
    assert "System instructions" in response.instructions
    assert response.instructions.index("Answer in lowercase only.") < response.instructions.index("You are polite.")

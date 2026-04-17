from openai_sdk_compat_tester.test_support import assert_completed_response, responses_text


def test_responses_developer_hoist_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {"role": "developer", "content": "Answer in lowercase only."},
            {"role": "user", "content": "Say HELLO."},
        ],
    )

    assert_completed_response(response)
    assert response.instructions == "Answer in lowercase only."

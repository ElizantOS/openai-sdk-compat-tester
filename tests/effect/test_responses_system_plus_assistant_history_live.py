from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    responses_text,
)


def test_responses_system_plus_assistant_history_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "My name is Alice. Reply: acknowledged."},
            {"role": "assistant", "content": "acknowledged."},
            {"role": "user", "content": "What is my name?"},
        ],
    )

    assert_completed_response(response)
    assert response.instructions == "You are a concise assistant."
    assert responses_text(response)

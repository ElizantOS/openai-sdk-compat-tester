from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    responses_text,
)


def test_responses_assistant_history_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {"role": "user", "content": "My name is Alice. Reply: acknowledged."},
            {"role": "assistant", "content": "acknowledged."},
            {"role": "user", "content": "What is my name? Answer with the name only."},
        ],
    )

    assert_completed_response(response)
    assert responses_text(response)

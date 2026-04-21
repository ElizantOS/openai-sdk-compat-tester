from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    responses_text,
)


def test_responses_string_input_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input="Say hello in exactly 3 words.",
    )

    assert_completed_response(response)
    assert responses_text(response)

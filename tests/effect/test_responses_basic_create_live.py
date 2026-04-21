from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    response_conversation_input,
    responses_output_types,
    responses_text,
)


def test_responses_basic_create_live(live_client, model_name: str, turn_mode: str):
    response = live_client.responses.create(
        model=model_name,
        input=response_conversation_input(
            {"role": "user", "content": "Say hello in exactly 3 words."},
            turn_mode,
        ),
    )

    assert_completed_response(response)
    assert "message" in responses_output_types(response)
    assert responses_text(response)

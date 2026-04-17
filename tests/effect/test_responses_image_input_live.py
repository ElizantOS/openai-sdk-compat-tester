from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
    response_conversation_input,
    response_image_input_parts,
    responses_text,
)


def test_responses_image_input_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[
            {
                "role": "user",
                "content": response_image_input_parts("What do you see in this image? Answer in one sentence."),
            }
        ],
    )

    assert_completed_response(response)
    assert responses_text(response)

from openai_sdk_compat_tester.test_support import (
    RED_SQUARE_PNG_BASE64,
    conversation_messages,
    response_text,
)


def test_content_mixed_parts_order(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=16,
        messages=conversation_messages([
            {
                "role": "developer",
                "content": (
                    "Read the user's content parts in order. "
                    "Reply exactly in the form first|color|second using lowercase ASCII."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "alpha"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{RED_SQUARE_PNG_BASE64}",
                            "detail": "low",
                        },
                    },
                    {"type": "text", "text": "omega"},
                ],
            },
        ], turn_mode),
    )

    assert response_text(response).strip().lower() == "alpha|red|omega"

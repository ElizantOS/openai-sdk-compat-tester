from openai_sdk_compat_tester.test_support import (
    RED_SQUARE_PNG_BASE64,
    conversation_messages,
    response_text,
)


def test_vision_base64(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=5,
        messages=conversation_messages(
            [
                {
                    "role": "developer",
                    "content": "You are a color classifier. Output exactly one lowercase English word: red, green, blue, or other.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify the dominant color of the image and output only one word.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{RED_SQUARE_PNG_BASE64}",
                                "detail": "low",
                            },
                        },
                    ],
                },
            ],
            turn_mode,
        ),
    )

    text = response_text(response).strip().lower()
    assert response.object == "chat.completion"
    assert text in {"red", "green", "blue", "other"}
    assert text == "red"

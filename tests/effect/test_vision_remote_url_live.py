from openai_chat_compat_tester.test_support import DEFAULT_RED_REMOTE_IMAGE_URL, response_text
from openai_chat_compat_tester.test_support import conversation_messages


def test_vision_remote_url(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=5,
        messages=conversation_messages([
            {
                "role": "developer",
                "content": "You are a color classifier. Output exactly one lowercase English word: red, green, blue, or other.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify the dominant color of the image and output only one word."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": DEFAULT_RED_REMOTE_IMAGE_URL,
                            "detail": "low",
                        },
                    },
                ],
            },
        ], turn_mode),
    )

    text = response_text(response).strip().lower()
    assert response.object == "chat.completion"
    assert text == "red"

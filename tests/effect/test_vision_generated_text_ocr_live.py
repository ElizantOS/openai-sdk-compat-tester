from openai_chat_compat_tester.test_support import GENERATED_OCR_TEXT, make_text_image_data_url, response_text
from openai_chat_compat_tester.test_support import conversation_messages


def test_vision_generated_text_ocr(live_client, model_name, turn_mode):
    data_url = make_text_image_data_url(GENERATED_OCR_TEXT)

    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=12,
        messages=conversation_messages([
            {
                "role": "developer",
                "content": "You are an OCR tool. Output only the uppercase ASCII text in the image. No explanation and no extra spaces.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Read the text in the image and output only the text itself."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                            "detail": "low",
                        },
                    },
                ],
            },
        ], turn_mode),
    )

    text = response_text(response).strip().upper().replace(" ", "")
    assert response.object == "chat.completion"
    assert text == GENERATED_OCR_TEXT

import json

from openai_chat_compat_tester.test_support import conversation_messages


def test_content_assistant_array_output(live_client, model_name, turn_mode):
    raw = live_client.chat.completions.with_raw_response.create(
        model=model_name,
        temperature=0,
        max_tokens=8,
        messages=conversation_messages(
            [
                {"role": "developer", "content": "Reply exactly with: hello world"},
                {"role": "user", "content": "Do it."},
            ],
            turn_mode,
        ),
    )

    payload = json.loads(raw.text)
    content = payload["choices"][0]["message"]["content"]

    assert isinstance(content, list)
    assert content
    text_parts = [
        part.get("text", "")
        for part in content
        if part.get("type") in {"text", "output_text"}
    ]
    assert "".join(text_parts).strip() == "hello world"

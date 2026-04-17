import json

from openai_sdk_compat_tester.test_support import (
    conversation_messages,
    looks_like_json_object,
)


def test_chat_response_format_json_object(live_client, model_name, turn_mode):
    baseline_messages = conversation_messages(
        [
            {
                "role": "system",
                "content": "Answer in plain English prose. Do not use JSON, braces, or key-value syntax.",
            },
            {
                "role": "user",
                "content": "Write one plain sentence saying that Alice lives in London.",
            },
        ],
        turn_mode,
    )

    baseline = live_client.chat.completions.create(
        model=model_name,
        messages=baseline_messages,
        max_tokens=60,
    )
    baseline_content = baseline.choices[0].message.content or ""
    assert not looks_like_json_object(baseline_content)

    json_messages = conversation_messages(
        [
            {
                "role": "system",
                "content": (
                    "You are a structured data formatter. When JSON object output is requested, "
                    "return only valid JSON and follow the user's requested fields exactly."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return a JSON object with exactly two keys: name and city. "
                    "Set name to Alice and city to London. Do not include any other keys."
                ),
            },
        ],
        turn_mode,
    )

    response = live_client.chat.completions.create(
        model=model_name,
        messages=json_messages,
        response_format={"type": "json_object"},
        max_tokens=100,
    )

    content = (response.choices[0].message.content or "").strip()
    assert looks_like_json_object(content)

    parsed = json.loads(content)
    assert isinstance(parsed, dict)
    assert set(parsed.keys()) == {"name", "city"}
    assert str(parsed["name"]).lower() == "alice"
    assert str(parsed["city"]).lower() == "london"

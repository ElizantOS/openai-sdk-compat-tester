import json

from openai_chat_compat_tester.test_support import (
    conversation_messages,
    looks_like_json_object,
)


def test_chat_response_format_json_object(live_client, model_name, turn_mode):
    messages = conversation_messages([
        {
            "role": "developer",
            "content": "Unless structured output is explicitly requested, answer in plain natural language with no JSON.",
        },
        {
            "role": "user",
            "content": "Provide the person's name Alice and city London.",
        },
    ], turn_mode)

    baseline = live_client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=60,
    )
    baseline_content = baseline.choices[0].message.content or ""
    assert not looks_like_json_object(baseline_content)

    response = live_client.chat.completions.create(
        model=model_name,
        messages=messages,
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

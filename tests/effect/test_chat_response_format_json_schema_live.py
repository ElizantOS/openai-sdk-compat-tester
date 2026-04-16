import json

from openai_chat_compat_tester.test_support import (
    conversation_messages,
    looks_like_json_object,
)


def test_chat_response_format_json_schema(live_client, model_name, turn_mode):
    schema = {
        "name": "person_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "city": {"type": "string"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
            },
            "required": ["name", "city", "priority"],
            "additionalProperties": False,
        },
    }

    messages = conversation_messages([
        {
            "role": "developer",
            "content": "Unless structured output is explicitly requested, answer in plain natural language with no JSON.",
        },
        {
            "role": "user",
            "content": "Provide the person's name Alice, city London, and priority medium.",
        },
    ], turn_mode)

    baseline = live_client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=80,
    )
    baseline_content = baseline.choices[0].message.content or ""
    assert not looks_like_json_object(baseline_content)

    response = live_client.chat.completions.create(
        model=model_name,
        messages=messages,
        response_format={"type": "json_schema", "json_schema": schema},
        max_tokens=150,
    )

    content = (response.choices[0].message.content or "").strip()
    assert looks_like_json_object(content)

    parsed = json.loads(content)
    assert set(parsed.keys()) == {"name", "city", "priority"}
    assert isinstance(parsed["name"], str)
    assert isinstance(parsed["city"], str)
    assert isinstance(parsed["priority"], str)
    assert parsed["name"].lower() == "alice"
    assert parsed["city"].lower() == "london"
    assert parsed["priority"] == "medium"

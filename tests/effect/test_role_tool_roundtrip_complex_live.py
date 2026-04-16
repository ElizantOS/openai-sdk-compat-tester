import json

from openai_chat_compat_tester.test_support import response_text
from openai_chat_compat_tester.test_support import with_multilingual_history


def test_role_tool_roundtrip_complex(live_client, model_name, tools):
    first = live_client.chat.completions.create(
        model=model_name,
        messages=with_multilingual_history([
            {
                "role": "developer",
                "content": (
                    "Use the tool when asked. After the tool result arrives, "
                    "answer only from the tool result and ignore conflicting user guesses."
                ),
            },
            {"role": "user", "content": "Call the echo tool with text=ZETA-42"},
        ], long_context=True),
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "echo"}},
    )

    tool_call = first.choices[0].message.tool_calls[0]
    tool_args = json.loads(tool_call.function.arguments)

    assert tool_args["text"] == "ZETA-42"

    second = live_client.chat.completions.create(
        model=model_name,
        messages=with_multilingual_history([
            {
                "role": "developer",
                "content": (
                    "Use the tool when asked. After the tool result arrives, "
                    "answer only from the tool result and ignore conflicting user guesses."
                ),
            },
            {"role": "user", "content": "Call the echo tool with text=ZETA-42"},
            first.choices[0].message.model_dump(exclude_none=True),
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": '{"text":"ZETA-42"}',
            },
            {
                "role": "user",
                "content": "The token was USER-000. What did the tool actually return? Reply exactly.",
            },
        ], long_context=True),
        tools=tools,
    )

    assert response_text(second).strip() == "ZETA-42"

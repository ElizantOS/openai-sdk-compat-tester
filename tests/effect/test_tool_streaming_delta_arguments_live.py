import json

from openai_sdk_compat_tester.test_support import conversation_messages


def test_tool_streaming_delta_arguments(live_client, model_name, turn_mode):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo structured input.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "city": {"type": "string"},
                        "mode": {"type": "string"},
                    },
                    "required": ["text", "city", "mode"],
                    "additionalProperties": False,
                },
            },
        }
    ]

    stream = live_client.chat.completions.create(
        model=model_name,
        stream=True,
        messages=conversation_messages(
            [
                {"role": "system", "content": "Use the tool when asked."},
                {
                    "role": "user",
                    "content": "Call echo with text='hello world from streaming delta test', city='Shanghai', mode='loud'",
                },
            ],
            turn_mode,
        ),
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "echo"}},
    )

    argument_fragments = []
    tool_name = None
    finish_reason = None
    for chunk in stream:
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        if choice.finish_reason is not None:
            finish_reason = choice.finish_reason
        for tool_call in choice.delta.tool_calls or []:
            if tool_call.function.name:
                tool_name = tool_call.function.name
            if tool_call.function.arguments:
                argument_fragments.append(tool_call.function.arguments)

    assert tool_name == "echo"
    assert len(argument_fragments) >= 2

    parsed = json.loads("".join(argument_fragments))
    assert parsed["text"] == "hello world from streaming delta test"
    assert parsed["city"] == "Shanghai"
    assert parsed["mode"] == "loud"
    assert finish_reason == "tool_calls"

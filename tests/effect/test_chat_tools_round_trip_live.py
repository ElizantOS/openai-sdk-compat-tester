from openai_sdk_compat_tester.test_support import with_multilingual_history


def test_chat_tools_round_trip(live_client, model_name, tools):
    first = live_client.chat.completions.create(
        model=model_name,
        messages=with_multilingual_history(
            [
                {
                    "role": "system",
                    "content": "Use the tool when asked, then answer briefly after the tool result arrives.",
                },
                {"role": "user", "content": "Call the echo tool with text=hello"},
            ],
            long_context=True,
        ),
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "echo"}},
    )

    tool_calls = first.choices[0].message.tool_calls
    assert tool_calls is not None
    assert len(tool_calls) == 1
    tool_call = tool_calls[0]

    second = live_client.chat.completions.create(
        model=model_name,
        messages=with_multilingual_history(
            [
                {
                    "role": "system",
                    "content": "Use the tool when asked, then answer briefly after the tool result arrives.",
                },
                {"role": "user", "content": "Call the echo tool with text=hello"},
                first.choices[0].message.model_dump(exclude_none=True),
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": '{"text":"hello"}',
                },
            ],
            long_context=True,
        ),
        tools=tools,
    )

    assert second.choices[0].message.role == "assistant"
    assert (second.choices[0].message.content or "").strip()

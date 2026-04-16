from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_tools_named_choice_multi(live_client, model_name, tools_multi, turn_mode):
    completion = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [
                {"role": "system", "content": "Use the tool when asked."},
                {"role": "user", "content": "Call the echo tool with text=hello"},
            ],
            turn_mode,
        ),
        tools=tools_multi,
        tool_choice={"type": "function", "function": {"name": "echo"}},
    )

    assert completion.choices[0].finish_reason == "tool_calls"
    tool_calls = completion.choices[0].message.tool_calls
    assert tool_calls is not None
    assert len(tool_calls) == 1
    assert tool_calls[0].function.name == "echo"

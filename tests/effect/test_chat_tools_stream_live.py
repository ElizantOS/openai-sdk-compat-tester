from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_tools_stream(live_client, model_name, tools, turn_mode):
    stream = live_client.chat.completions.create(
        model=model_name,
        stream=True,
        messages=conversation_messages([
            {"role": "system", "content": "Use the tool when asked."},
            {"role": "user", "content": "Call the echo tool with text=hello"},
        ], turn_mode),
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "echo"}},
    )

    saw_tool_call = False
    saw_tool_finish = False
    for chunk in stream:
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta
        if getattr(delta, "tool_calls", None):
            saw_tool_call = True
        if choice.finish_reason == "tool_calls":
            saw_tool_finish = True

    assert saw_tool_call
    assert saw_tool_finish

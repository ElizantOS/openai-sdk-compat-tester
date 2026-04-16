from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_parallel_tool_calls(live_client, model_name, turn_mode):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information.",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get the current time.",
                "parameters": {
                    "type": "object",
                    "properties": {"timezone": {"type": "string"}},
                    "required": ["timezone"],
                },
            },
        },
    ]

    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages([
            {
                "role": "user",
                "content": (
                    "Call both get_weather and get_time. "
                    "Use Shanghai for the city and Asia/Shanghai for the timezone. "
                    "Do not answer with plain text."
                ),
            }
        ], turn_mode),
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=True,
    )

    message = response.choices[0].message
    assert response.choices[0].finish_reason == "tool_calls"
    assert message.tool_calls is not None
    assert len(message.tool_calls) >= 2

    tool_names = {tool_call.function.name for tool_call in message.tool_calls}
    assert tool_names == {"get_weather", "get_time"}

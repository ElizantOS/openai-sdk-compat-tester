from openai_sdk_compat_tester.test_support import conversation_messages


def test_chat_stream_include_usage(live_client, model_name, turn_mode):
    stream = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [{"role": "user", "content": "Count from 1 to 5."}], turn_mode
        ),
        stream=True,
        stream_options={"include_usage": True},
        max_tokens=30,
    )

    usage_found = False
    for chunk in stream:
        if chunk.usage is not None:
            usage_found = True
            assert chunk.usage.completion_tokens > 0
    assert usage_found

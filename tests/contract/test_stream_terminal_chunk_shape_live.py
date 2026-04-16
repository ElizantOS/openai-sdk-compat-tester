from openai_chat_compat_tester.test_support import conversation_messages


def test_stream_terminal_chunk_shape(live_client, model_name, turn_mode):
    chunks = list(
        live_client.chat.completions.create(
            model=model_name,
            messages=conversation_messages(
                [{"role": "user", "content": "Count from 1 to 5."}], turn_mode
            ),
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=30,
        )
    )

    assert chunks

    last = chunks[-1]
    assert last.object == "chat.completion.chunk"
    assert last.usage is not None
    assert last.choices == []

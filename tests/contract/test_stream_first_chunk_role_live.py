from openai_chat_compat_tester.test_support import conversation_messages


def test_stream_first_chunk_role(live_client, model_name, turn_mode):
    stream = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [{"role": "user", "content": "Say hello."}], turn_mode
        ),
        stream=True,
        max_tokens=12,
    )

    chunks = [chunk for chunk in stream if chunk.choices]

    assert chunks

    role_indices = []
    for index, chunk in enumerate(chunks):
        role = getattr(chunk.choices[0].delta, "role", None)
        if role is not None:
            role_indices.append(index)

    assert role_indices
    assert role_indices[0] == 0
    assert chunks[0].choices[0].delta.role == "assistant"
    assert len(role_indices) == 1

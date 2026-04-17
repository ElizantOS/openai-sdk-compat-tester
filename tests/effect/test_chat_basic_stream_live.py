from openai_sdk_compat_tester.test_support import conversation_messages


def test_chat_basic_stream(live_client, model_name, turn_mode):
    stream = live_client.chat.completions.create(
        model=model_name,
        stream=True,
        messages=conversation_messages(
            [
                {"role": "system", "content": "Be terse."},
                {"role": "user", "content": "Reply with exactly: ok"},
            ],
            turn_mode,
        ),
    )

    chunks = []
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            chunks.append(delta.content)

    assert "".join(chunks) == "ok"

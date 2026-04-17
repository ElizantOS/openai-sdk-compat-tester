from openai_sdk_compat_tester.test_support import (
    conversation_messages,
    stream_text_deltas,
)


def test_stream_chunk_order(live_client, model_name, turn_mode):
    expected = "A|B|C|D|E"

    stream = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=16,
        stream=True,
        messages=conversation_messages(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a precise string emitter. "
                        "When the user asks for exact output, reproduce it character-for-character with no extra text."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Return the literal string {expected} exactly, character-for-character.",
                },
            ],
            turn_mode,
        ),
    )

    assert "".join(stream_text_deltas(stream)).strip() == expected

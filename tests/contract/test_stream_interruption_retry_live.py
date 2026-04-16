from openai_chat_compat_tester.test_support import stream_text_deltas
from openai_chat_compat_tester.test_support import with_multilingual_history


def test_stream_interruption_retry(live_client, model_name):
    kwargs = {
        "model": model_name,
        "stream": True,
        "temperature": 0,
        "max_tokens": 32,
        "messages": with_multilingual_history([
            {
                "role": "developer",
                "content": "Reply exactly with: 1 2 3 4 5 6 7 8 9 10",
            },
            {"role": "user", "content": "Do it."},
        ]),
    }

    interrupted_stream = live_client.chat.completions.create(**kwargs)
    first_fragment = ""
    for chunk in interrupted_stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            first_fragment = delta
            break
    close = getattr(interrupted_stream, "close", None)
    if callable(close):
        close()

    assert first_fragment

    retry_stream = live_client.chat.completions.create(**kwargs)
    full_output = "".join(stream_text_deltas(retry_stream)).strip()

    assert full_output == "1 2 3 4 5 6 7 8 9 10"
    assert full_output.startswith(first_fragment.strip())

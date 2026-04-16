from concurrent.futures import ThreadPoolExecutor

from openai_chat_compat_tester.test_support import (
    conversation_messages,
    response_text,
    stream_text_deltas,
)


def test_concurrent_seed_consistency(live_client, model_name, turn_mode):
    kwargs = {
        "model": model_name,
        "messages": conversation_messages(
            [
                {
                    "role": "user",
                    "content": "Generate one random-looking integer from 1 to 100 and explain it in one sentence.",
                }
            ],
            turn_mode,
        ),
        "temperature": 0,
        "seed": 42,
        "max_tokens": 40,
    }

    def run_once() -> str:
        return response_text(live_client.chat.completions.create(**kwargs)).strip()

    with ThreadPoolExecutor(max_workers=3) as executor:
        outputs = list(executor.map(lambda _: run_once(), range(3)))

    assert len(set(outputs)) == 1


def test_concurrent_stream_seed_consistency(live_client, model_name, turn_mode):
    kwargs = {
        "model": model_name,
        "messages": conversation_messages(
            [
                {
                    "role": "user",
                    "content": "Reply exactly with: hello streaming seed",
                }
            ],
            turn_mode,
        ),
        "temperature": 0,
        "seed": 42,
        "max_tokens": 20,
        "stream": True,
    }

    def run_once() -> str:
        stream = live_client.chat.completions.create(**kwargs)
        return "".join(stream_text_deltas(stream)).strip()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outputs = list(executor.map(lambda _: run_once(), range(2)))

    assert outputs == ["hello streaming seed", "hello streaming seed"]

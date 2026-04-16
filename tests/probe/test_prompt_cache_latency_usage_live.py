import time

from openai_chat_compat_tester.test_support import response_text
from openai_chat_compat_tester.test_support import conversation_messages


def _normalize_cache_marker(text: str) -> str:
    return text.strip().rstrip(".")


def _raw_cached_request(live_client, **kwargs):
    start = time.perf_counter()
    raw = live_client.chat.completions.with_raw_response.create(**kwargs)
    elapsed = time.perf_counter() - start
    parsed = raw.parse()
    headers = dict(raw.headers)
    return parsed, headers, elapsed


def test_prompt_cache_latency_usage(live_client, model_name, turn_mode):
    kwargs = {
        "model": model_name,
        "prompt_cache_key": "compat-cache-latency-usage",
        "messages": conversation_messages([
            {"role": "system", "content": "Reply exactly with CACHE-PROBE-OK."},
            {"role": "user", "content": "Do it."},
        ], turn_mode),
        "temperature": 0,
        "max_tokens": 8,
    }

    samples = [_raw_cached_request(live_client, **kwargs) for _ in range(3)]
    texts = [_normalize_cache_marker(response_text(parsed)) for parsed, _, _ in samples]
    latencies_ms = [round(elapsed * 1000, 1) for _, _, elapsed in samples]
    header_keys = sorted({key.lower() for _, headers, _ in samples for key in headers.keys()})

    assert texts == ["CACHE-PROBE-OK"] * 3
    for parsed, _, _ in samples:
        assert parsed.usage is not None
        assert parsed.usage.total_tokens == parsed.usage.prompt_tokens + parsed.usage.completion_tokens

    print("prompt_cache latency ms:", latencies_ms)
    print("prompt_cache observed headers:", header_keys)

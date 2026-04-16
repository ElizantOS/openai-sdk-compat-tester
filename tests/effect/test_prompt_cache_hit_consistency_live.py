from openai_chat_compat_tester.test_support import response_text
from openai_chat_compat_tester.test_support import conversation_messages


def _normalize_cache_marker(text: str) -> str:
    return text.strip().rstrip(".")


def test_prompt_cache_hit_consistency(live_client, model_name, turn_mode):
    kwargs = {
        "model": model_name,
        "prompt_cache_key": "compat-cache-hit-consistency",
        "messages": conversation_messages([
            {"role": "system", "content": "Reply exactly with CACHE-CONSISTENT."},
            {"role": "user", "content": "Do it."},
        ], turn_mode),
        "temperature": 0,
        "max_tokens": 8,
    }

    first = live_client.chat.completions.create(**kwargs)
    second = live_client.chat.completions.create(**kwargs)

    first_text = _normalize_cache_marker(response_text(first))
    second_text = _normalize_cache_marker(response_text(second))

    assert first_text == "CACHE-CONSISTENT"
    assert second_text == "CACHE-CONSISTENT"
    assert first_text == second_text
    assert first.choices[0].finish_reason == second.choices[0].finish_reason

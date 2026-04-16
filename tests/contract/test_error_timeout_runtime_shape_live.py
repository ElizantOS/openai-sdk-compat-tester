import pytest
from openai import APITimeoutError


def test_error_timeout_runtime_shape(live_client, model_name):
    with pytest.raises(APITimeoutError):
        live_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Write a long essay about recursion."}],
            max_tokens=300,
            timeout=0.0001,
        )

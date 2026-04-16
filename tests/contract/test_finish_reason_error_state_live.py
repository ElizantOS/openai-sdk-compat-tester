import pytest
from openai import BadRequestError

from openai_chat_compat_tester.test_support import assert_error_response


def test_finish_reason_error_state(live_client, model_name):
    with pytest.raises(BadRequestError) as excinfo:
        live_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=-1,
        )

    payload = assert_error_response(excinfo.value)
    assert "choices" not in payload
    assert "error" in payload

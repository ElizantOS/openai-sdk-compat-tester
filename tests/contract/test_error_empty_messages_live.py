import pytest
from openai import BadRequestError

from openai_chat_compat_tester.test_support import assert_invalid_request_response


def test_error_empty_messages(live_client, model_name):
    with pytest.raises(BadRequestError) as excinfo:
        live_client.chat.completions.create(
            model=model_name,
            messages=[],
        )

    error = assert_invalid_request_response(excinfo.value)
    assert error.get("message")

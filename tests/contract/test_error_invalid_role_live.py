import pytest
from openai import BadRequestError

from openai_sdk_compat_tester.test_support import assert_invalid_request_response


def test_error_invalid_role(live_client, model_name):
    with pytest.raises(BadRequestError) as excinfo:
        live_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "not-a-real-role", "content": "hello"}],
        )

    error = assert_invalid_request_response(excinfo.value)
    assert error.get("message")

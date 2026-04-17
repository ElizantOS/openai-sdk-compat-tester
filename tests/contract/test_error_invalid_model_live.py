import pytest
from openai import BadRequestError

from openai_sdk_compat_tester.test_support import assert_invalid_request_response


def test_error_invalid_model(live_client):
    with pytest.raises(BadRequestError) as excinfo:
        live_client.chat.completions.create(
            model="this-model-does-not-exist-123456",
            messages=[{"role": "user", "content": "hi"}],
        )

    error = assert_invalid_request_response(excinfo.value)
    assert error.get("message")

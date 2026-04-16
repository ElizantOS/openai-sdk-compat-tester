import pytest
from openai import BadRequestError

from openai_chat_compat_tester.test_support import assert_invalid_request_response


def test_error_invalid_response_schema(live_client, model_name):
    with pytest.raises(BadRequestError) as excinfo:
        live_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Return JSON."}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "bad_schema",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": "this-should-be-an-object",
                    },
                },
            },
        )

    error = assert_invalid_request_response(excinfo.value)
    assert error.get("message")

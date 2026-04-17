import pytest
from openai import BadRequestError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error


def test_responses_invalid_token_limit_error_live(live_client, model_name: str):
    with pytest.raises(BadRequestError) as exc_info:
        live_client.responses.create(
            model=model_name,
            input=[{"role": "user", "content": "Say hello."}],
            max_output_tokens=0,
        )

    assert_openai_error(
        exc_info.value,
        status_code=400,
        error_type="routing_error",
        error_code="invalid_request",
        message_substring="max_output_tokens must be greater than 0",
    )

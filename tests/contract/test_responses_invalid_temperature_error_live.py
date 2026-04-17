import pytest
from openai import BadRequestError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error


def test_responses_invalid_temperature_error_live(live_client, model_name: str):
    with pytest.raises(BadRequestError) as exc_info:
        live_client.responses.create(
            model=model_name,
            input=[{"role": "user", "content": "Say hello."}],
            temperature=3,
        )

    assert_openai_error(
        exc_info.value,
        status_code=400,
        error_type="routing_error",
        error_code="invalid_request",
        message_substring="temperature must be between 0 and 2",
    )

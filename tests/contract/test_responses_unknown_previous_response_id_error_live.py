import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
)


def test_responses_unknown_previous_response_id_error_live(live_client, model_name: str):
    with pytest.raises(InternalServerError) as exc_info:
        live_client.responses.create(
            model=model_name,
            previous_response_id="resp_missing_for_sdk_test",
            input=[{"role": "user", "content": "What is my name?"}],
        )

    assert_openai_error(
        exc_info.value,
        status_code=502,
        error_type="routing_error",
        error_code="upstream_request_failed",
        message_substring="unknown previous_response_id",
    )

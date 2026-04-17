import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import assert_openai_error


def test_responses_streaming_invalid_input_item_type_error_live(live_client, model_name: str):
    with pytest.raises(InternalServerError) as exc_info:
        with live_client.responses.stream(
            model=model_name,
            input=[{"type": "weird", "role": "user", "content": "hi"}],
        ) as stream:
            for _ in stream:
                pass

    assert_openai_error(
        exc_info.value,
        status_code=502,
        error_type="routing_error",
        error_code="upstream_request_failed",
        message_substring="Invalid value: 'weird'",
    )

import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error, responses_text


def test_responses_json_object_without_json_prompt_error_live(live_client, model_name: str):
    with pytest.raises(InternalServerError) as exc_info:
        live_client.responses.create(
            model=model_name,
            input=[{"role": "user", "content": "Say hello."}],
            text={"format": {"type": "json_object"}},
        )

    assert_openai_error(
        exc_info.value,
        status_code=502,
        error_type="routing_error",
        error_code="upstream_request_failed",
        message_substring="must contain the word 'json'",
    )

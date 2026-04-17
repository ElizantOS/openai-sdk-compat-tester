import pytest
from openai import InternalServerError

from openai_sdk_compat_tester.test_support import assert_openai_error


def test_responses_top_p_compat_gap_error_live(live_client, model_name: str):
    with pytest.raises(InternalServerError) as exc_info:
        live_client.responses.create(
            model=model_name,
            input=[{"role": "user", "content": "Say hello."}],
            top_p=0.9,
        )

    assert_openai_error(
        exc_info.value,
        status_code=502,
        error_type="routing_error",
        error_code="upstream_request_failed",
        message_substring="Unsupported parameter: top_p",
    )

import pytest
from openai import BadRequestError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error


def test_responses_reasoning_effort_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        extra_body={"reasoning_effort": "low"},
    )

    assert_completed_response(response)
    assert response.reasoning.effort == "low"

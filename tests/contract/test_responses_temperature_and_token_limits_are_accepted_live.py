import pytest
from openai import BadRequestError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error


def test_responses_temperature_and_token_limits_are_accepted_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello in exactly 3 words."}],
        temperature=0.2,
        max_output_tokens=42,
        extra_body={"max_tokens": 42, "max_completion_tokens": 42},
    )

    assert_completed_response(response)

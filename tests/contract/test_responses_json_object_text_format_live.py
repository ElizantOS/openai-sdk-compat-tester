import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import assert_completed_response, assert_openai_error, responses_text


def test_responses_json_object_text_format_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Return a JSON object with one key named ok."}],
        text={"format": {"type": "json_object"}},
    )

    assert_completed_response(response)
    text = responses_text(response)
    assert text.startswith("{")
    assert text.endswith("}")

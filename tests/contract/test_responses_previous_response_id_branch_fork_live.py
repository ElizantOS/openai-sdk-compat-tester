import pytest
from openai import InternalServerError
from openai_sdk_compat_tester.test_support import (
    RESPONSES_WEATHER_TOOL,
    assert_completed_response,
    assert_openai_error,
)


def test_responses_previous_response_id_branch_fork_live(live_client, model_name: str):
    parent = live_client.responses.create(model=model_name, input=[{"role": "user", "content": "Start a branchable context."}])
    short_branch = live_client.responses.create(
        model=model_name,
        previous_response_id=parent.id,
        input=[{"role": "user", "content": "Make it shorter."}],
    )
    translation_branch = live_client.responses.create(
        model=model_name,
        previous_response_id=parent.id,
        input=[{"role": "user", "content": "Translate it to Chinese."}],
    )

    assert_completed_response(short_branch)
    assert_completed_response(translation_branch)
    assert short_branch.prompt_cache_key != translation_branch.prompt_cache_key

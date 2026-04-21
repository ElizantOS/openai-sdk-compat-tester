from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
)


def test_responses_previous_response_id_branch_idempotence_live(live_client, model_name: str):
    parent = live_client.responses.create(model=model_name, input=[{"role": "user", "content": "Start a branchable context."}])
    first_branch = live_client.responses.create(
        model=model_name,
        previous_response_id=parent.id,
        input=[{"role": "user", "content": "Summarize the previous answer."}],
    )
    second_branch = live_client.responses.create(
        model=model_name,
        previous_response_id=parent.id,
        input=[{"role": "user", "content": "Summarize the previous answer."}],
    )

    assert_completed_response(first_branch)
    assert_completed_response(second_branch)
    assert first_branch.prompt_cache_key == second_branch.prompt_cache_key

from openai_sdk_compat_tester.test_support import (
    assert_completed_response,
)


def test_responses_text_verbosity_live(live_client, model_name: str):
    response = live_client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": "Say hello."}],
        text={"verbosity": "high"},
    )

    assert_completed_response(response)
    assert response.text.verbosity == "high"

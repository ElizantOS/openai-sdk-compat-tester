from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_logprobs(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [{"role": "user", "content": "Say hello"}], turn_mode
        ),
        logprobs=True,
        top_logprobs=3,
        max_tokens=10,
    )

    logprobs = response.choices[0].logprobs
    assert logprobs is not None
    assert logprobs.content

    first = logprobs.content[0]
    assert first.token
    assert isinstance(first.logprob, float)
    assert first.top_logprobs is not None
    assert len(first.top_logprobs) <= 3
    if first.top_logprobs:
        assert first.top_logprobs[0].token

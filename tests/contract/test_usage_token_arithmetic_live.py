from openai_chat_compat_tester.test_support import conversation_messages


def test_usage_token_arithmetic(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=16,
        messages=conversation_messages([{"role": "user", "content": "Say hello in one short sentence."}], turn_mode),
    )

    usage = response.usage

    assert usage is not None
    assert usage.total_tokens == usage.prompt_tokens + usage.completion_tokens

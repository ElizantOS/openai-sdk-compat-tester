from openai_sdk_compat_tester.test_support import conversation_messages


def test_chat_n_completions(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [{"role": "user", "content": "Say hello in one word."}], turn_mode
        ),
        n=3,
        max_tokens=10,
    )

    assert len(response.choices) == 3
    for choice in response.choices:
        assert choice.message.content

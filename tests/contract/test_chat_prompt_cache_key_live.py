from openai_sdk_compat_tester.test_support import conversation_messages


def test_chat_prompt_cache_key(live_client, model_name, turn_mode):
    completion = live_client.chat.completions.create(
        model=model_name,
        prompt_cache_key="python-sdk-chat-test",
        messages=conversation_messages(
            [
                {"role": "system", "content": "Be terse."},
                {"role": "user", "content": "Reply with exactly: ok"},
            ],
            turn_mode,
        ),
    )

    assert completion.choices[0].message.content == "ok"

from openai_sdk_compat_tester.test_support import conversation_messages, response_text


def test_chat_seed_consistency(live_client, model_name, turn_mode):
    messages = conversation_messages(
        [
            {
                "role": "user",
                "content": (
                    "Generate a random-looking integer between 1 and 100 "
                    "and explain the choice in one sentence."
                ),
            }
        ],
        turn_mode,
    )

    params = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 50,
        "temperature": 0.0,
        "seed": 42,
    }

    response_one = live_client.chat.completions.create(**params)
    response_two = live_client.chat.completions.create(**params)

    assert response_text(response_one).strip() == response_text(response_two).strip()

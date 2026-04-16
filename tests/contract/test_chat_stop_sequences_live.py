from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_stop_sequences(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [
                {
                    "role": "user",
                    "content": "Describe Shanghai's weather and major attractions in detail, and make the answer fairly long.",
                }
            ],
            turn_mode,
        ),
        stop=["。", "！", "？"],
        max_tokens=150,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    assert content

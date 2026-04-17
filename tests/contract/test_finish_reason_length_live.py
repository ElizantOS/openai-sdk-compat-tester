from openai_sdk_compat_tester.test_support import conversation_messages


def test_finish_reason_length(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=1,
        messages=conversation_messages(
            [
                {
                    "role": "developer",
                    "content": (
                        "Reply with exactly this ten-word string: "
                        "one two three four five six seven eight nine ten"
                    ),
                },
                {"role": "user", "content": "Do it."},
            ],
            turn_mode,
        ),
    )

    assert response.choices[0].finish_reason == "length"

from openai_chat_compat_tester.test_support import conversation_messages


def test_chat_frequency_presence_penalty_acceptance(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages([
            {"role": "developer", "content": "Reply exactly with: hello world"},
            {"role": "user", "content": "Do it."},
        ], turn_mode),
        temperature=0,
        frequency_penalty=2.0,
        presence_penalty=2.0,
        max_tokens=8,
    )

    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert (response.choices[0].message.content or "").strip()

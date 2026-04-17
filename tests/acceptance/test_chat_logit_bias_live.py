from openai_sdk_compat_tester.test_support import conversation_messages


def test_chat_logit_bias_acceptance(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages(
            [{"role": "user", "content": "Say hello or hi"}], turn_mode
        ),
        logit_bias={50256: 100},
        max_tokens=10,
    )

    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert (response.choices[0].message.content or "").strip()

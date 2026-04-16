from openai_chat_compat_tester.test_support import conversation_messages


def test_usage_content_scale(live_client, model_name, turn_mode):
    short_prompt = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=4,
        messages=conversation_messages([{"role": "user", "content": "hi"}], turn_mode),
    )
    long_prompt = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=4,
        messages=conversation_messages(
            [{"role": "user", "content": " ".join(["hello"] * 200)}], turn_mode
        ),
    )

    assert long_prompt.usage.prompt_tokens > short_prompt.usage.prompt_tokens

    short_completion = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=8,
        messages=conversation_messages(
            [
                {"role": "developer", "content": "Reply exactly with OK."},
                {"role": "user", "content": "Do it."},
            ],
            turn_mode,
        ),
    )
    long_completion = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=40,
        messages=conversation_messages(
            [
                {
                    "role": "developer",
                    "content": (
                        "Reply exactly with: alpha beta gamma delta epsilon zeta "
                        "eta theta iota kappa lambda mu"
                    ),
                },
                {"role": "user", "content": "Do it."},
            ],
            turn_mode,
        ),
    )

    assert (
        long_completion.usage.completion_tokens
        >= short_completion.usage.completion_tokens
    )

from openai_sdk_compat_tester.test_support import conversation_messages

LONG_COMPLETION_TEXT = (
    "token01 token02 token03 token04 token05 token06 token07 token08 "
    "token09 token10 token11 token12 token13 token14 token15 token16 "
    "token17 token18 token19 token20 token21 token22 token23 token24 "
    "token25 token26 token27 token28 token29 token30 token31 token32 "
    "token33 token34 token35 token36 token37 token38 token39 token40"
)


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
                {
                    "role": "system",
                    "content": "You are an exact text emitter. Return only the requested text.",
                },
                {"role": "user", "content": "Return exactly this text and nothing else: OK"},
            ],
            turn_mode,
        ),
    )
    long_completion = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=80,
        messages=conversation_messages(
            [
                {
                    "role": "system",
                    "content": "You are an exact text emitter. Return only the requested text.",
                },
                {
                    "role": "user",
                    "content": f"Return exactly this text and nothing else: {LONG_COMPLETION_TEXT}",
                },
            ],
            turn_mode,
        ),
    )

    assert (
        long_completion.usage.completion_tokens
        >= short_completion.usage.completion_tokens
    )

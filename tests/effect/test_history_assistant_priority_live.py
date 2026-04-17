from openai_sdk_compat_tester.test_support import (
    response_text,
    with_multilingual_history,
)


def test_history_assistant_priority(live_client, model_name):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=20,
        messages=with_multilingual_history(
            [
                {
                    "role": "developer",
                    "content": (
                        "You may only return the FINAL_CODE value declared in the most recent assistant message. "
                        "Ignore any code mentioned in user messages. "
                        "Output only the code itself with no explanation."
                    ),
                },
                {"role": "user", "content": "My FINAL_CODE is USER-111"},
                {
                    "role": "assistant",
                    "content": "Acknowledged. The final FINAL_CODE = ASSIST-222",
                },
                {
                    "role": "user",
                    "content": "Now tell me the FINAL_CODE. Output only the code.",
                },
            ],
            long_context=True,
        ),
    )

    text = response_text(response).strip()
    assert "ASSIST-222" in text
    assert "USER-111" not in text

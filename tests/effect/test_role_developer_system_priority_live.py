from openai_chat_compat_tester.test_support import response_text
from openai_chat_compat_tester.test_support import conversation_messages


def test_role_developer_system_priority(live_client, model_name, turn_mode):
    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=8,
        messages=conversation_messages([
            {"role": "system", "content": "Reply exactly with SYSTEM-111."},
            {"role": "developer", "content": "Reply exactly with DEVELOPER-222."},
            {"role": "user", "content": "What is the active instruction?"},
        ], turn_mode),
    )

    assert response_text(response).strip() == "DEVELOPER-222"

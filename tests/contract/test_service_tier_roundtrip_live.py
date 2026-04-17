from openai_sdk_compat_tester.test_support import (
    ALLOWED_SERVICE_TIERS,
    conversation_messages,
)


def _requested_service_tiers():
    return ("auto", "default")


def test_service_tier_roundtrip(live_client, model_name, turn_mode):
    for requested_tier in _requested_service_tiers():
        response = live_client.chat.completions.create(
            model=model_name,
            temperature=0,
            max_tokens=8,
            service_tier=requested_tier,
            messages=conversation_messages([{"role": "user", "content": "Reply with exactly ok."}], turn_mode),
        )

        actual_tier = getattr(response, "service_tier", None)
        assert response.object == "chat.completion"
        assert actual_tier in ALLOWED_SERVICE_TIERS
        assert actual_tier == requested_tier

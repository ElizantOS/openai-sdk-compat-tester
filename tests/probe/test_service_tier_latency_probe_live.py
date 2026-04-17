import statistics
import time

from openai_sdk_compat_tester.test_support import ALLOWED_SERVICE_TIERS, conversation_messages


def test_service_tier_latency_probe(live_client, model_name, turn_mode):
    tiers = ["auto", "default"]
    rounds = 3
    samples = {}

    for tier in tiers:
        samples[tier] = []
        for _ in range(rounds):
            start = time.perf_counter()
            response = live_client.chat.completions.create(
                model=model_name,
                temperature=0,
                max_tokens=12,
                service_tier=tier,
                messages=conversation_messages(
                    [{"role": "user", "content": "Reply with exactly ping."}], turn_mode
                ),
            )
            elapsed = time.perf_counter() - start
            actual_tier = getattr(response, "service_tier", None)
            assert actual_tier in ALLOWED_SERVICE_TIERS
            samples[tier].append(elapsed)

    summary = {
        tier: {
            "median_ms": round(statistics.median(values) * 1000, 1),
            "min_ms": round(min(values) * 1000, 1),
            "max_ms": round(max(values) * 1000, 1),
        }
        for tier, values in samples.items()
    }
    print("service_tier latency summary:", summary)

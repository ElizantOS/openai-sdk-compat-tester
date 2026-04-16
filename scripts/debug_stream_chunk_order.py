#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openai_chat_compat_tester.live_config import choose_model_id
from openai_chat_compat_tester.test_support import conversation_messages

EXPECTED = "A|B|C|D|E"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Debug raw SSE frames for the stream chunk order compatibility case."
    )
    parser.add_argument("--attempts", type=int, default=10, help="How many requests to send before stopping.")
    parser.add_argument(
        "--turn-mode",
        choices=("single-turn", "multi-turn"),
        default="single-turn",
        help="Which turn-mode variant to debug.",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop after the first mismatched assembled response.",
    )
    parser.add_argument(
        "--sleep-ms",
        type=int,
        default=200,
        help="Delay between attempts.",
    )
    return parser.parse_args()


def resolve_model_id(client: httpx.Client, base_url: str) -> str:
    configured_model = os.getenv("OPENAI_COMPAT_MODEL", "").strip()
    response = client.get(f"{base_url}/models")
    response.raise_for_status()
    payload = response.json()
    entries = payload.get("data", []) if isinstance(payload, dict) else []
    model_ids = [entry.get("id", "").strip() for entry in entries if isinstance(entry, dict) and entry.get("id")]
    model, _ = choose_model_id(model_ids, configured_model)
    return model


def main() -> int:
    args = parse_args()
    base_url = os.getenv("OPENAI_COMPAT_BASE_URL", "http://127.0.0.1:18080/v1").rstrip("/")
    api_key = os.getenv("OPENAI_COMPAT_API_KEY", "compat-test")
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client(timeout=30.0, trust_env=False, headers=headers) as client:
        model = resolve_model_id(client, base_url)
        print(f"base_url={base_url}")
        print(f"model={model}")
        print(f"turn_mode={args.turn_mode}")
        print(f"expected={EXPECTED}")

        for attempt in range(1, args.attempts + 1):
            request_payload = {
                "model": model,
                "temperature": 0,
                "max_tokens": 16,
                "stream": True,
                "messages": conversation_messages(
                    [
                        {
                            "role": "system",
                            "content": (
                                "You are a precise string emitter. "
                                "When the user asks for exact output, reproduce it character-for-character with no extra text."
                            ),
                        },
                        {"role": "user", "content": f"Return the literal string {EXPECTED} exactly, character-for-character."},
                    ],
                    args.turn_mode,
                ),
            }

            print(f"\n=== attempt {attempt} ===")
            assembled_parts: list[str] = []
            done = False

            with client.stream("POST", f"{base_url}/chat/completions", json=request_payload) as response:
                print(f"status={response.status_code}")
                for raw_line in response.iter_lines():
                    if raw_line is None:
                        continue
                    line = raw_line if isinstance(raw_line, str) else raw_line.decode("utf-8", "replace")
                    if not line:
                        continue
                    print(line)
                    if line == "data: [DONE]":
                        done = True
                        continue
                    if not line.startswith("data: "):
                        continue
                    event = json.loads(line[6:])
                    for choice in event.get("choices", []):
                        delta = choice.get("delta") or {}
                        content = delta.get("content")
                        if content:
                            assembled_parts.append(content)

            assembled = "".join(assembled_parts).strip()
            print(f"assembled={assembled}")
            print(f"done={done}")
            success = assembled == EXPECTED and done
            print(f"success={success}")

            if args.stop_on_failure and not success:
                return 1
            if attempt < args.attempts and args.sleep_ms > 0:
                time.sleep(args.sleep_ms / 1000)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

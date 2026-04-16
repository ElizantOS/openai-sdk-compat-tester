from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Capability:
    slug: str
    category: str
    name: str
    status: str
    test_file: str | None = None
    notes: str = ""


def capability_suite(capability: Capability) -> str:
    if capability.test_file is None:
        return "unknown"
    parts = Path(capability.test_file).parts
    if len(parts) >= 3 and parts[0] == "tests":
        return parts[1]
    return "unknown"


def capability_expectation(capability: Capability) -> str:
    suite = capability_suite(capability)
    if suite == "effect":
        return "strict-pass"
    if suite == "contract":
        return "format-accurate"
    if suite == "acceptance":
        return "input-no-error"
    if suite == "probe":
        return "probe"
    return "unknown"


def find_capability(slug: str) -> Capability | None:
    for capability in CAPABILITIES:
        if capability.slug == slug:
            return capability
    return None


CAPABILITIES = [
    # Effect
    Capability(
        slug="chat-basic-non-stream",
        category="Basic Chat",
        name="Basic non-stream chat completion",
        status="covered",
        test_file="tests/effect/test_chat_basic_non_stream_live.py",
    ),
    Capability(
        slug="chat-basic-stream",
        category="Basic Chat",
        name="Basic streaming chat completion",
        status="covered",
        test_file="tests/effect/test_chat_basic_stream_live.py",
    ),
    Capability(
        slug="chat-tool-calling-non-stream",
        category="Tool Calling",
        name="Function/tool calling in non-stream mode",
        status="covered",
        test_file="tests/effect/test_chat_tools_non_stream_live.py",
    ),
    Capability(
        slug="chat-tool-calling-stream",
        category="Tool Calling",
        name="Function/tool calling in stream mode",
        status="covered",
        test_file="tests/effect/test_chat_tools_stream_live.py",
    ),
    Capability(
        slug="chat-tool-round-trip",
        category="Tool Calling",
        name="Tool call followed by tool result round-trip",
        status="covered",
        test_file="tests/effect/test_chat_tools_round_trip_live.py",
    ),
    Capability(
        slug="chat-tool-choice-named-multi",
        category="Tool Calling",
        name="Named tool choice with multiple available tools",
        status="covered",
        test_file="tests/effect/test_chat_tools_named_choice_multi_live.py",
    ),
    Capability(
        slug="chat-parallel-tool-calls",
        category="Tool Calling",
        name="Parallel tool call request compatibility",
        status="covered",
        test_file="tests/effect/test_chat_parallel_tool_calls_live.py",
    ),
    Capability(
        slug="tool-streaming-delta-arguments",
        category="Tool Streaming",
        name="Streaming tool_call deltas and partial argument assembly",
        status="covered",
        test_file="tests/effect/test_tool_streaming_delta_arguments_live.py",
    ),
    Capability(
        slug="chat-json-object-output",
        category="Structured Output",
        name="JSON object response format",
        status="covered",
        test_file="tests/effect/test_chat_response_format_json_object_live.py",
    ),
    Capability(
        slug="chat-json-schema-output",
        category="Structured Output",
        name="JSON schema constrained response format",
        status="covered",
        test_file="tests/effect/test_chat_response_format_json_schema_live.py",
    ),
    Capability(
        slug="chat-stop-semantic-effect",
        category="Sampling and Control",
        name="Stop sequence semantic truncation effect",
        status="covered",
        test_file="tests/effect/test_stop_effect_live.py",
    ),
    Capability(
        slug="chat-seed-determinism",
        category="Sampling and Control",
        name="Deterministic repeated output with seed",
        status="covered",
        test_file="tests/effect/test_chat_seed_consistency_live.py",
    ),
    Capability(
        slug="chat-penalty-controls",
        category="Sampling and Control",
        name="Frequency and presence penalty accepted by chat adapter",
        status="covered",
        test_file="tests/acceptance/test_chat_frequency_presence_penalty_live.py",
        notes="accepted by adapter; not counted as native semantic effect support",
    ),
    Capability(
        slug="chat-multiple-candidates",
        category="Sampling and Control",
        name="Multiple candidates via n completions",
        status="covered",
        test_file="tests/effect/test_chat_n_completions_live.py",
    ),
    Capability(
        slug="vision-base64-image",
        category="Vision",
        name="Vision with base64 image_url input",
        status="covered",
        test_file="tests/effect/test_vision_base64_live.py",
    ),
    Capability(
        slug="vision-generated-text-ocr",
        category="Vision",
        name="Vision OCR against a dynamically generated local image",
        status="covered",
        test_file="tests/effect/test_vision_generated_text_ocr_live.py",
    ),
    Capability(
        slug="vision-remote-image-url",
        category="Vision",
        name="Vision with remote image_url input",
        status="covered",
        test_file="tests/effect/test_vision_remote_url_live.py",
    ),
    Capability(
        slug="chat-input-audio",
        category="Multimodal Audio",
        name="Chat content parts with input_audio payloads",
        status="covered",
        test_file="tests/effect/test_chat_input_audio_live.py",
    ),
    Capability(
        slug="multi-turn-assistant-history",
        category="Conversation History",
        name="Assistant-message history priority in multi-turn chat",
        status="covered",
        test_file="tests/effect/test_history_assistant_priority_live.py",
    ),
    Capability(
        slug="content-array-mixed-parts",
        category="Content Shapes",
        name="Mixed content parts ordering (text + image + text)",
        status="covered",
        test_file="tests/effect/test_content_mixed_parts_order_live.py",
    ),
    Capability(
        slug="assistant-content-array-output",
        category="Content Shapes",
        name="Assistant content array output compatibility",
        status="covered",
        test_file="tests/effect/test_content_assistant_array_output_live.py",
    ),
    Capability(
        slug="developer-system-priority",
        category="Roles",
        name="developer vs system priority and precedence",
        status="covered",
        test_file="tests/effect/test_role_developer_system_priority_live.py",
    ),
    Capability(
        slug="tool-role-roundtrip-depth",
        category="Roles",
        name="Tool-role round-trip beyond the basic echo path",
        status="covered",
        test_file="tests/effect/test_role_tool_roundtrip_complex_live.py",
    ),
    Capability(
        slug="prompt-cache-hit-consistency",
        category="Prompt Caching",
        name="Prompt cache hit preserves semantic output consistency",
        status="covered",
        test_file="tests/effect/test_prompt_cache_hit_consistency_live.py",
    ),
    Capability(
        slug="concurrent-seed-consistency",
        category="Concurrency and Idempotency",
        name="Concurrent requests with the same seed remain deterministic",
        status="covered",
        test_file="tests/effect/test_concurrent_seed_consistency_live.py",
    ),
    # Contract
    Capability(
        slug="models-listing",
        category="Model Listing",
        name="List models via the OpenAI-compatible models endpoint",
        status="covered",
        test_file="tests/contract/test_models_live.py",
    ),
    Capability(
        slug="chat-prompt-cache-key",
        category="Basic Chat",
        name="Stable prompt cache key handling",
        status="covered",
        test_file="tests/contract/test_chat_prompt_cache_key_live.py",
    ),
    Capability(
        slug="chat-stop-parameter",
        category="Sampling and Control",
        name="Stop parameter acceptance",
        status="covered",
        test_file="tests/contract/test_chat_stop_sequences_live.py",
    ),
    Capability(
        slug="chat-logprobs",
        category="Sampling and Control",
        name="Logprobs and top_logprobs response compatibility",
        status="covered",
        test_file="tests/contract/test_chat_logprobs_live.py",
    ),
    Capability(
        slug="chat-stream-usage",
        category="Sampling and Control",
        name="Streaming usage blocks with include_usage",
        status="covered",
        test_file="tests/contract/test_chat_stream_include_usage_live.py",
    ),
    Capability(
        slug="chat-reasoning-effort",
        category="Sampling and Control",
        name="Reasoning effort parameter",
        status="covered",
        test_file="tests/contract/test_chat_reasoning_effort_live.py",
        notes="May be skipped when the selected model or backend does not support it.",
    ),
    Capability(
        slug="service-tier-roundtrip",
        category="Service Tier",
        name="service_tier request/response round-trip",
        status="covered",
        test_file="tests/contract/test_service_tier_roundtrip_live.py",
    ),
    Capability(
        slug="finish-reason-length",
        category="Finish Reasons",
        name="Explicit finish_reason coverage for length truncation",
        status="covered",
        test_file="tests/contract/test_finish_reason_length_live.py",
    ),
    Capability(
        slug="finish-reason-content-filter",
        category="Finish Reasons",
        name="Observed finish_reason behavior for content-filter-like refusals",
        status="covered",
        test_file="tests/probe/test_finish_reason_content_filter_live.py",
        notes="Probe only; many providers emit a refusal text with stop instead of content_filter.",
    ),
    Capability(
        slug="finish-reason-failure-surface",
        category="Finish Reasons",
        name="Failure-path behavior does not masquerade as a normal completion finish_reason",
        status="covered",
        test_file="tests/contract/test_finish_reason_error_state_live.py",
    ),
    Capability(
        slug="error-invalid-model",
        category="Errors and Boundaries",
        name="Invalid model handling",
        status="covered",
        test_file="tests/contract/test_error_invalid_model_live.py",
    ),
    Capability(
        slug="error-empty-messages",
        category="Errors and Boundaries",
        name="Empty messages handling",
        status="covered",
        test_file="tests/contract/test_error_empty_messages_live.py",
    ),
    Capability(
        slug="error-invalid-role",
        category="Errors and Boundaries",
        name="Invalid role handling",
        status="covered",
        test_file="tests/contract/test_error_invalid_role_live.py",
    ),
    Capability(
        slug="error-invalid-tool-schema",
        category="Errors and Boundaries",
        name="Invalid tool schema handling",
        status="covered",
        test_file="tests/contract/test_error_invalid_tool_schema_live.py",
    ),
    Capability(
        slug="error-invalid-response-schema",
        category="Errors and Boundaries",
        name="Invalid response schema handling",
        status="covered",
        test_file="tests/contract/test_error_invalid_response_schema_live.py",
    ),
    Capability(
        slug="error-timeout-runtime-shape",
        category="Errors and Boundaries",
        name="Timeout and runtime error surface compatibility",
        status="covered",
        test_file="tests/contract/test_error_timeout_runtime_shape_live.py",
        notes="Uses a very small client timeout to verify timeout surfacing through the official SDK.",
    ),
    Capability(
        slug="streaming-first-chunk-role",
        category="Streaming Semantics",
        name="Role emitted only on the first streaming chunk",
        status="covered",
        test_file="tests/contract/test_stream_first_chunk_role_live.py",
    ),
    Capability(
        slug="streaming-chunk-order",
        category="Streaming Semantics",
        name="Streaming chunk ordering remains stable",
        status="covered",
        test_file="tests/contract/test_stream_chunk_order_live.py",
    ),
    Capability(
        slug="streaming-terminal-chunk-shape",
        category="Streaming Semantics",
        name="Terminal streaming chunk shape matches OpenAI semantics",
        status="covered",
        test_file="tests/contract/test_stream_terminal_chunk_shape_live.py",
    ),
    Capability(
        slug="stream-interruption-retry",
        category="Streaming Semantics",
        name="Streaming interruption and retry semantics",
        status="covered",
        test_file="tests/contract/test_stream_interruption_retry_live.py",
    ),
    Capability(
        slug="usage-token-arithmetic",
        category="Usage Accounting",
        name="Prompt/completion/total token arithmetic consistency",
        status="covered",
        test_file="tests/contract/test_usage_token_arithmetic_live.py",
    ),
    Capability(
        slug="usage-content-scale",
        category="Usage Accounting",
        name="Prompt and completion token counts scale with content size",
        status="covered",
        test_file="tests/contract/test_usage_content_scale_live.py",
    ),
    # Probe
    Capability(
        slug="service-tier-latency-probe",
        category="Service Tier",
        name="service_tier latency probe",
        status="covered",
        test_file="tests/probe/test_service_tier_latency_probe_live.py",
    ),
    Capability(
        slug="prompt-cache-latency-usage",
        category="Prompt Caching",
        name="Prompt cache latency and usage observability probe",
        status="covered",
        test_file="tests/probe/test_prompt_cache_latency_usage_live.py",
        notes="Probe-oriented test; it records observability rather than asserting absolute latency improvement.",
    ),
    # Acceptance-only planned exception
    Capability(
        slug="chat-logit-bias-semantic",
        category="Sampling and Control",
        name="Acceptance-only logit_bias validation",
        status="covered",
        test_file="tests/acceptance/test_chat_logit_bias_live.py",
        notes="Validates request acceptance and normal response shape only; it does not assert semantic effect.",
    ),
    Capability(
        slug="chat-temperature-acceptance",
        category="Sampling and Control",
        name="Acceptance-only temperature validation",
        status="covered",
        test_file="tests/acceptance/test_chat_temperature_live.py",
        notes="Validates request acceptance and normal response shape only; it does not assert semantic temperature effect.",
    ),
]

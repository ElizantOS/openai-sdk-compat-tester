import ast
from pathlib import Path

from openai_chat_compat_tester.scenarios import CAPABILITIES


def test_scenario_ids_are_unique():
    ids = [capability.slug for capability in CAPABILITIES]
    assert len(ids) == len(set(ids))


def test_capability_test_files_exist():
    root = Path(__file__).resolve().parents[1]
    for capability in CAPABILITIES:
        if capability.test_file is None:
            continue
        assert (root / capability.test_file).exists()


def test_effect_conversation_coverage_rule_is_explicit():
    root = Path(__file__).resolve().parents[1]
    effect_dir = root / "tests" / "effect"
    # Keep this guard file-based: the effect suite intentionally keeps one primary
    # live scenario per file, so file-level `turn_mode` coverage is a stable proxy.
    intrinsically_multi_turn_files = {
        "test_chat_tools_round_trip_live.py",
        "test_history_assistant_priority_live.py",
        "test_role_tool_roundtrip_complex_live.py",
    }

    for path in sorted(effect_dir.glob("test_*_live.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        uses_turn_mode = any(isinstance(node, ast.Name) and node.id == "turn_mode" for node in ast.walk(tree))
        if path.name in intrinsically_multi_turn_files:
            # These scenarios already encode a longer multi-turn exchange directly,
            # so they should stay as explicit exceptions instead of using turn_mode.
            assert not uses_turn_mode, f"{path.name} should stay an explicit intrinsic multi-turn exception"
            continue
        assert uses_turn_mode, f"{path.name} should cover both single-turn and multi-turn variants"

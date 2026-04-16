import json

from rich.console import Console

from openai_chat_compat_tester.cli import _build_json_report
from openai_chat_compat_tester.cli import _render_tui
from openai_chat_compat_tester.cli import _print_run_report
from openai_chat_compat_tester.cli import _selected_capabilities
from openai_chat_compat_tester.cli import _write_output
from openai_chat_compat_tester.scenarios import CAPABILITIES
from openai_chat_compat_tester.scenarios import capability_suite


def test_capability_suites_are_recognized():
    suites = {capability_suite(capability) for capability in CAPABILITIES}
    assert {"effect", "contract", "probe", "acceptance"} <= suites


def test_selected_capabilities_filter_by_suite():
    selected = _selected_capabilities("probe", {"covered"}, set())
    assert selected
    assert all(capability_suite(capability) == "probe" for capability in selected)


def test_run_report_shows_full_matrix_by_default(capsys):
    _print_run_report(
        {
            "chat-basic-non-stream": ("passed", 12.3, "1 passed in 0.10s"),
        },
        only_executed=False,
    )
    output = capsys.readouterr().out
    assert "Effect" in output
    assert "[passed][strict-pass] chat-basic-non-stream" in output
    assert "[not-run]" in output


def test_run_report_can_show_only_executed(capsys):
    _print_run_report(
        {
            "chat-basic-non-stream": ("passed", 12.3, "1 passed in 0.10s"),
        },
        only_executed=True,
    )
    output = capsys.readouterr().out
    assert "[passed][strict-pass] chat-basic-non-stream" in output
    assert "[not-run]" not in output
    assert "[todo]" not in output


def test_render_tui_outputs_live_panel(capsys):
    console = Console(file=None, force_terminal=False, width=120)
    _render_tui(
        {
            "chat-basic-non-stream": ("passed", 12.3, "1 passed in 0.10s"),
        },
        only_executed=True,
        started_at=0.0,
        console=console,
    )
    output = capsys.readouterr().out
    assert "OpenAI Chat Compat Tester" in output
    assert "Live view updates after each scenario." in output
    assert "chat-basic-non-stream" in output
    assert "[passed][strict-pass] 1 passed in 0.10s | chat-basic-non-stream (12.3ms)" in output


def test_render_tui_truncates_long_lines_instead_of_wrapping(capsys):
    console = Console(file=None, force_terminal=False, width=70)
    _render_tui(
        {
            "multi-turn-assistant-history": (
                "skipped",
                473.2,
                "1 skipped in 0.02s",
            ),
        },
        only_executed=True,
        started_at=0.0,
        console=console,
    )
    output = capsys.readouterr().out
    assert "1 skipped in 0.02s" in output
    assert "Assistant-message history" not in output
    assert "…" in output


def test_plain_report_keeps_summary_on_separate_line(capsys):
    _print_run_report(
        {
            "chat-basic-non-stream": ("passed", 12.3, "1 passed in 0.10s"),
        },
        only_executed=True,
    )
    output = capsys.readouterr().out
    assert "[passed][strict-pass] chat-basic-non-stream" in output
    assert "  1 passed in 0.10s" in output


def test_json_report_includes_counts_and_items():
    report = _build_json_report(
        {"chat-basic-non-stream": ("passed", 12.3, "1 passed in 0.10s")},
        only_executed=True,
        selected_slugs=["chat-basic-non-stream"],
    )
    assert report["tool"] == "openai-chat-compat"
    assert report["counts"]["passed"] == 1
    assert report["counts"]["total"] == 1
    assert report["items"][0]["slug"] == "chat-basic-non-stream"
    assert report["items"][0]["status"] == "passed"


def test_write_output_creates_parent_directory(tmp_path):
    target = tmp_path / "reports" / "report.json"
    payload = json.dumps({"ok": True})
    _write_output(str(target), payload)
    assert target.read_text() == payload

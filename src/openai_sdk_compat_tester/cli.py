from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from contextlib import nullcontext
from pathlib import Path

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .scenarios import (
    CAPABILITIES,
    capability_expectation,
    capability_suite,
    find_capability,
)

SUITES = ("effect", "contract", "probe", "acceptance")
API_MODES = ("chat", "responses", "all")


def _color(text: str, code: str) -> str:
    return f"\x1b[{code}m{text}\x1b[0m"


def _green(text: str) -> str:
    return _color(text, "32")


def _red(text: str) -> str:
    return _color(text, "31")


def _yellow(text: str) -> str:
    return _color(text, "33")


def _gray(text: str) -> str:
    return _color(text, "90")


def _status_icon(status: str) -> str:
    if status == "running":
        return _yellow("◉")
    if status == "passed":
        return _green("✓")
    if status == "failed":
        return _red("✗")
    if status == "skipped":
        return _yellow("◌")
    if status == "not-run":
        return _gray("·")
    if status == "todo":
        return _gray("…")
    return _gray("?")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="openai-sdk-compat")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List capability scenarios")
    list_parser.add_argument(
        "--suite",
        choices=(*SUITES, "all"),
        default="all",
        help="Filter by test suite",
    )
    list_parser.add_argument(
        "--api-mode",
        choices=API_MODES,
        default="chat",
        help="Filter by API mode",
    )
    list_parser.add_argument(
        "--status",
        choices=("covered", "todo", "all"),
        default="all",
        help="Filter by scenario status",
    )

    run_parser = subparsers.add_parser("run", help="Run capability scenarios")
    run_parser.add_argument(
        "--suite",
        choices=(*SUITES, "all"),
        default="all",
        help="Run only one test suite",
    )
    run_parser.add_argument(
        "--api-mode",
        choices=API_MODES,
        default="chat",
        help="Run only one API mode",
    )
    run_parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Run only specific capability slug(s). Repeatable.",
    )
    run_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print pytest output for each executed scenario",
    )
    run_parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failure",
    )
    run_parser.add_argument(
        "--only-executed",
        action="store_true",
        help="Show only executed scenarios instead of the full project matrix",
    )
    run_parser.add_argument(
        "--tui",
        action="store_true",
        help="Force interactive TUI rendering",
    )
    run_parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable TUI and use plain streaming output",
    )
    run_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render the final report as plain text or JSON",
    )
    run_parser.add_argument(
        "--output",
        help="Write the final report to a file path",
    )

    parser.set_defaults(command="list")
    return parser.parse_args(argv)


def _selected_capabilities(suite: str, statuses: set[str], slugs: set[str], api_mode: str = "chat") -> list:
    selected = []
    for capability in CAPABILITIES:
        if api_mode != "all" and capability.api_mode != api_mode:
            continue
        if capability.status not in statuses:
            continue
        if suite != "all" and capability_suite(capability) != suite:
            continue
        if slugs and capability.slug not in slugs:
            continue
        selected.append(capability)
    return selected


def _print_capabilities(capabilities: list) -> None:
    for capability in capabilities:
        suite = capability_suite(capability)
        expectation = capability_expectation(capability)
        notes = f" - {capability.notes}" if capability.notes else ""
        suffix = f" ({capability.test_file})" if capability.test_file else ""
        print(
            f"[{capability.status}][{capability.api_mode}][{suite}][{expectation}] {capability.category} / {capability.name}{suffix}{notes}"
        )


def _run_one(capability, verbose: bool) -> tuple[str, float, str]:
    if capability.test_file is None:
        return "unknown", 0.0, "scenario has no test_file"

    env = os.environ.copy()
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        capability.test_file,
    ]
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        capture_output=True,
        text=True,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    output = (proc.stdout + "\n" + proc.stderr).strip()

    status = "failed"
    if proc.returncode == 0:
        if " skipped" in output:
            status = "skipped"
        else:
            status = "passed"

    if verbose and output:
        print(output)

    summary = ""
    if output:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if lines:
            summary = lines[-1]
    return status, elapsed_ms, summary


def _suite_label(suite: str) -> str:
    return {
        "effect": "Effect",
        "contract": "Contract",
        "probe": "Probe",
        "acceptance": "Acceptance",
    }.get(suite, suite.title())


def _all_capabilities_for_report(only_executed: bool, executed_slugs: set[str]) -> list:
    if only_executed:
        return [capability for capability in CAPABILITIES if capability.slug in executed_slugs]
    return CAPABILITIES


def _build_run_report_lines(
    results: dict[str, tuple[str, float, str]], *, only_executed: bool, inline_summary: bool = False
) -> list[str]:
    visible = _all_capabilities_for_report(only_executed, set(results.keys()))
    counters = {"running": 0, "passed": 0, "failed": 0, "skipped": 0, "not-run": 0, "todo": 0}
    lines: list[str] = []

    for suite in SUITES:
        suite_capabilities = [capability for capability in visible if capability_suite(capability) == suite]
        if not suite_capabilities:
            continue

        lines.append(_suite_label(suite))
        for capability in suite_capabilities:
            if capability.slug in results:
                status, elapsed_ms, summary = results[capability.slug]
                counters[status] += 1
                expectation = capability_expectation(capability)
                line = (
                    f"{_status_icon(status)} [{status}][{expectation}] "
                    f"[{capability.api_mode}] {capability.slug} ({elapsed_ms}ms) - {capability.name}"
                )
                if summary and inline_summary:
                    line = (
                        f"{_status_icon(status)} [{status}][{expectation}] "
                        f"{summary} | [{capability.api_mode}] {capability.slug} ({elapsed_ms}ms) - {capability.name}"
                    )
                lines.append(line)
                if summary and not inline_summary:
                    lines.append(f"  {summary}")
                continue

            if capability.status == "todo":
                counters["todo"] += 1
                lines.append(
                    f"{_status_icon('todo')} [todo][{capability_expectation(capability)}] "
                    f"[{capability.api_mode}] {capability.slug} - {capability.name}"
                )
            else:
                counters["not-run"] += 1
                lines.append(
                    f"{_status_icon('not-run')} [not-run][{capability_expectation(capability)}] "
                    f"[{capability.api_mode}] {capability.slug} - {capability.name}"
                )
        lines.append("")

    total = sum(counters.values())
    lines.append(
        "Results: "
        f"{_yellow(str(counters['running']) + ' running')}, "
        f"{_green(str(counters['passed']) + ' passed')}, "
        f"{_red(str(counters['failed']) + ' failed')}, "
        f"{_yellow(str(counters['skipped']) + ' skipped')}, "
        f"{_gray(str(counters['not-run']) + ' not-run')}, "
        f"{_gray(str(counters['todo']) + ' todo')}, "
        f"{total} total"
    )
    return lines


def _print_run_report(results: dict[str, tuple[str, float, str]], *, only_executed: bool) -> None:
    for line in _build_run_report_lines(results, only_executed=only_executed):
        print(line)


def _report_items(results: dict[str, tuple[str, float, str]], *, only_executed: bool) -> list[dict[str, object]]:
    visible = _all_capabilities_for_report(only_executed, set(results.keys()))
    items: list[dict[str, object]] = []
    for capability in visible:
        if capability.slug in results:
            status, elapsed_ms, summary = results[capability.slug]
        elif capability.status == "todo":
            status, elapsed_ms, summary = "todo", 0.0, ""
        else:
            status, elapsed_ms, summary = "not-run", 0.0, ""
        items.append(
            {
                "slug": capability.slug,
                "name": capability.name,
                "category": capability.category,
                "api_mode": capability.api_mode,
                "suite": capability_suite(capability),
                "expectation": capability_expectation(capability),
                "status": status,
                "elapsed_ms": elapsed_ms,
                "summary": summary,
                "test_file": capability.test_file,
                "notes": capability.notes,
            }
        )
    return items


def _report_counts(items: list[dict[str, object]]) -> dict[str, int]:
    counts = {"passed": 0, "failed": 0, "skipped": 0, "not-run": 0, "todo": 0, "running": 0}
    for item in items:
        status = item["status"]
        if status in counts:
            counts[status] += 1
    counts["total"] = len(items)
    return counts


def _build_json_report(
    results: dict[str, tuple[str, float, str]], *, only_executed: bool, selected_slugs: list[str]
) -> dict[str, object]:
    items = _report_items(results, only_executed=only_executed)
    return {
        "tool": "openai-sdk-compat",
        "report_format": "json",
        "selected_slugs": selected_slugs,
        "only_executed": only_executed,
        "counts": _report_counts(items),
        "items": items,
    }


def _write_output(path: str, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def _ansi_line_text(line: str) -> Text:
    text = Text.from_ansi(line)
    text.no_wrap = True
    text.overflow = "ellipsis"
    return text


def _build_tui_renderable(
    results: dict[str, tuple[str, float, str]], *, only_executed: bool, started_at: float
):
    elapsed = round(time.perf_counter() - started_at, 1)
    report_lines = _build_run_report_lines(results, only_executed=only_executed, inline_summary=True)
    report = Group(*(_ansi_line_text(line) for line in report_lines))
    return Group(
        Panel(
            Group(
                Text("OpenAI SDK Compat Tester", style="bold cyan", no_wrap=True, overflow="ellipsis"),
                Text(f"elapsed={elapsed}s", style="cyan", no_wrap=True, overflow="ellipsis"),
                Text(
                    "Press Ctrl+C to stop. Live view updates after each scenario.",
                    style="dim",
                    no_wrap=True,
                    overflow="ellipsis",
                ),
            ),
            border_style="cyan",
        ),
        Panel(report, title="Status", border_style="blue"),
    )


def _render_tui(
    results: dict[str, tuple[str, float, str]], *, only_executed: bool, started_at: float, console: Console | None = None
) -> None:
    active_console = console or Console()
    active_console.print(_build_tui_renderable(results, only_executed=only_executed, started_at=started_at))


def _update_live_tui(
    live: Live, results: dict[str, tuple[str, float, str]], *, only_executed: bool, started_at: float
) -> None:
    live.update(_build_tui_renderable(results, only_executed=only_executed, started_at=started_at), refresh=True)


def _run_capabilities(
    capabilities: list,
    verbose: bool,
    fail_fast: bool,
    only_executed: bool,
    tui: bool,
    output_format: str,
    output_path: str | None,
) -> int:
    passed = 0
    failed = 0
    skipped = 0
    results: dict[str, tuple[str, float, str]] = {}
    started_at = time.perf_counter()

    live_context = (
        Live(
            _build_tui_renderable(results, only_executed=only_executed, started_at=started_at),
            console=Console(),
            auto_refresh=False,
            transient=False,
        )
        if tui
        else nullcontext()
    )

    with live_context as live:
        try:
            for capability in capabilities:
                expectation = capability_expectation(capability)
                if tui and live is not None:
                    results[capability.slug] = ("running", 0.0, "")
                    _update_live_tui(live, results, only_executed=only_executed, started_at=started_at)
                else:
                    print(
                        f"{_status_icon('running')} [running][{expectation}] {capability.slug} - {capability.name}",
                        flush=True,
                    )

                status, elapsed_ms, summary = _run_one(capability, verbose=verbose)
                results[capability.slug] = (status, elapsed_ms, summary)

                if tui and live is not None:
                    _update_live_tui(live, results, only_executed=only_executed, started_at=started_at)
                else:
                    print(
                        f"{_status_icon(status)} [{status}][{expectation}] {capability.slug} ({elapsed_ms}ms) - {capability.name}",
                        flush=True,
                    )
                    if summary:
                        print(f"  {summary}", flush=True)

                if status == "passed":
                    passed += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    if fail_fast:
                        break
        finally:
            if tui and live is not None:
                _update_live_tui(live, results, only_executed=only_executed, started_at=started_at)

    selected_slugs = [capability.slug for capability in capabilities]
    if output_format == "json":
        report = json.dumps(
            _build_json_report(results, only_executed=only_executed, selected_slugs=selected_slugs),
            indent=2,
            sort_keys=True,
        )
        if output_path:
            _write_output(output_path, report + "\n")
        else:
            print(report)
    else:
        if not tui:
            _print_run_report(results, only_executed=only_executed)
        if output_path:
            text_report = "\n".join(_build_run_report_lines(results, only_executed=only_executed)) + "\n"
            _write_output(output_path, text_report)
    return 1 if failed > 0 else 0


def main() -> None:
    args = _parse_args(sys.argv[1:])

    if args.command == "list":
        status = getattr(args, "status", "all")
        suite = getattr(args, "suite", "all")
        api_mode = getattr(args, "api_mode", "chat")
        statuses = {"covered", "todo"} if status == "all" else {status}
        capabilities = _selected_capabilities(suite, statuses, set(), api_mode)
        _print_capabilities(capabilities)
        return

    if args.command == "run":
        unknown = [slug for slug in args.slug if find_capability(slug) is None]
        if unknown:
            print(_red(f"Unknown capability slug(s): {', '.join(unknown)}"), file=sys.stderr)
            raise SystemExit(2)

        capabilities = _selected_capabilities(
            args.suite,
            {"covered"},
            set(args.slug),
            args.api_mode,
        )
        if not capabilities:
            print(_yellow("No matching covered capabilities selected."))
            return
        tui = args.tui or (sys.stdout.isatty() and not args.plain and not args.verbose)
        raise SystemExit(
            _run_capabilities(
                capabilities,
                verbose=args.verbose,
                fail_fast=args.fail_fast,
                only_executed=args.only_executed,
                tui=tui,
                output_format=args.format,
                output_path=args.output,
            )
        )


if __name__ == "__main__":
    main()

# Contributing

Thanks for helping improve OpenAI Chat Compat Tester.

## Development

```bash
uv sync --extra dev
uv run pytest -q
```

If you prefer `venv` + `pip`, the README includes that path as well.

## Change Guidelines

- Keep compatibility claims evidence-based.
- Prefer adding or strengthening tests before broad refactors.
- Preserve the meaning of the result classes: `Effect`, `Contract`, `Probe`, and `Acceptance-only`.
- Keep capability slugs stable once published.
- Update `README.md` and `README_ZH.md` when user-facing behavior changes.

## Pull Requests

- Include a short explanation of the compatibility behavior or contract being changed.
- Add or update tests for any CLI or scenario-catalog behavior change.
- Mention any live-test limitations or provider-specific gaps explicitly.


# Changelog

## Unreleased

- Prepared the project for standalone open-source release with improved packaging metadata, contributor docs, CI scaffolding, and machine-readable CLI reporting.
- Renamed the runtime package and CLI entrypoint to `openai_sdk_compat_tester` / `openai-sdk-compat`.
- Added Responses API effect, contract, probe, and acceptance coverage alongside Chat Completions coverage.
- Added `--api-mode all` inventory and run support for combined Chat Completions + Responses compatibility matrices.
- Hardened prompt-sensitive live scenarios for smaller/faster models by keeping roles in `system` messages and exact task data in `user` messages.

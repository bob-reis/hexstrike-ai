# Repository Guidelines

## Project Structure & Module Organization
- `hexstrike_server.py` hosts the FastMCP Flask API and orchestrator; extend capabilities inside the existing section headers to keep routing predictable.
- `hexstrike_mcp.py` is the agent client; register new tools, health probes, and status reporters here so external agents discover them automatically.
- Helper scripts (`hexstrike_mcp_wrapper.sh`, `test_wrapper.sh`), diagnostics, and assets stay at the repository root alongside `assets/` and EnumDNS captures; avoid committing transient files such as `hexstrike.log`.

## Build, Test, and Development Commands
- `python3 -m venv hexstrike-env && source hexstrike-env/bin/activate` sets up the expected virtualenv for wrappers and automation.
- `pip install -r requirements.txt` installs Flask, FastMCP, Selenium, mitmproxy, and other orchestration dependencies; rerun after modifying Python tooling.
- `python3 hexstrike_server.py --help` documents server flags; use `HEXSTRIKE_HOST` / `HEXSTRIKE_PORT` to override the default `127.0.0.1:8888` bind.
- `python3 hexstrike_mcp.py --status` or `./test_wrapper.sh` provides a quick MCP reachability check before deeper testing.

## Coding Style & Naming Conventions
- Target Python 3.8+, PEP 8 spacing with four-space indents, and keep lines under ~110 chars unless readability suffers.
- Modules use `snake_case.py`, classes `CamelCase`, constants `UPPER_SNAKE`, and new public functions should include type hints.
- Route tool launches through `resolve_tool_command()` after updating `TOOL_EXECUTABLES`, and log events with the shared `logger` instead of print statements.

## Testing Guidelines
- `python3 test_mcp_simple.py` verifies FastMCP wiring and ensures the `hello_world` tool stays reachable.
- `python3 test_tool_resolution.py` exercises `/opt` tool lookups; investigate any emoji-prefixed failures before shipping.
- Run `pytest -q` for assertion suites, colocating new tests with feature code and stubbing external binaries or network calls.

## Commit & Pull Request Guidelines
- Follow the repo’s history: concise, single-line, present-tense commit subjects (e.g., `fix prowler path swap`).
- Collapse WIP commits, reference issue IDs where relevant, and list the exact test commands executed in the PR body.
- Describe affected tools or endpoints, note new CLI switches, and attach terminal snippets or screenshots for user-visible changes.

## Security & Configuration Tips
- Keep secrets out of source control; rely on environment variables or per-user config files.
- Validate new `/opt` integrations in disposable environments and document quirks in `TOOL_VENV_INTEGRATION.md`.
- Maintain restrictive network defaults (`127.0.0.1`, TLS when available) and call out any deviations during review.

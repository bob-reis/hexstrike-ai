# Repository Guidelines

## Project Structure & Module Organization
The FastMCP server lives in `hexstrike_server.py`, while the agent client and tool registry sit in `hexstrike_mcp.py`. Helper wrappers (`hexstrike_mcp_wrapper.sh`, `test_wrapper.sh`), diagnostics, and EnumDNS captures stay at the repo root next to `assets/`. Persist new utilities under `assets/` or a clearly named subfolder, and keep transient artifacts like `hexstrike.log` out of version control.

## Build, Test, and Development Commands
Create the standard environment with `python3 -m venv hexstrike-env && source hexstrike-env/bin/activate`, then install dependencies via `pip install -r requirements.txt`. Run `python3 hexstrike_server.py --help` to inspect server flags or override binds with `HEXSTRIKE_HOST` / `HEXSTRIKE_PORT`. Use `python3 hexstrike_mcp.py --status` or `./test_wrapper.sh` for a fast MCP reachability check before launching automation.

## Coding Style & Naming Conventions
Target Python 3.8+, four-space indents, and keep lines under ~110 characters unless clarity benefits otherwise. Modules remain `snake_case.py`, classes `CamelCase`, constants `UPPER_SNAKE`, and public functions include type hints. Route tool invocations through `resolve_tool_command()` after updating `TOOL_EXECUTABLES`, and always log with the shared `logger` instead of raw `print` calls.

## Testing Guidelines
`python3 test_mcp_simple.py` validates the FastMCP handshake and ensures the `hello_world` tool stays reachable. `python3 test_tool_resolution.py` verifies `/opt` resolution paths; investigate any emoji-prefixed failures immediately. Run `pytest -q` for unit coverage, colocating new tests beside related modules and stubbing external binaries or network calls.

## Commit & Pull Request Guidelines
Use concise, present-tense commit subjects (e.g., `fix prowler path swap`) and squash WIP history before raising a PR. Reference issue IDs when applicable, describe affected tools or endpoints, and note any new CLI flags. Include the exact test commands executed and attach terminal snippets or screenshots for user-visible changes.

## Security & Configuration Tips
Keep secrets in environment variables or per-user config files, never in source. Validate new `/opt` integrations inside disposable environments and document quirks in `TOOL_VENV_INTEGRATION.md`. Maintain the default loopback bind (`127.0.0.1`) unless coordinated otherwise, and call out any security-impacting deviations during review.

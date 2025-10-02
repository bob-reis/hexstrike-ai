#!/usr/bin/env python3
"""
Test script for tool resolution functionality
"""

# Tool executable mappings for /opt tools with virtual environments
TOOL_EXECUTABLES = {
    "docker-bench-security": "cd /opt/docker-bench-security && ./docker-bench-security.sh",
    "kube-hunter": "/opt/kube-hunter/venv/bin/python /opt/kube-hunter/kube-hunter.py",
    "kube-hunter-venv": "/opt/kube-hunter/venv/bin/python /opt/kube-hunter/kube-hunter.py",
    "prowler": "/opt/prowler/prowlwer-venv/bin/prowler",
    "prowler-alt": "python3 /opt/prowler/prowler.py",
    "ScoutSuite": "/opt/ScoutSuite/venv/bin/python /opt/ScoutSuite/scout.py",
    "scout-suite": "/opt/ScoutSuite/venv/bin/python /opt/ScoutSuite/scout.py",
    "volatility3": "/opt/volatility3/volatility-env/bin/python /opt/volatility3/vol.py",
    "vol.py": "/opt/volatility3/volatility-env/bin/python /opt/volatility3/vol.py",
    "vol": "/opt/volatility3/volatility-env/bin/python /opt/volatility3/vol.py",
    "enumdns": "/usr/bin/enumdns",
    "stegsolve": "java -jar /opt/stegsolve/StegSolve.jar",
}

TOOL_ALIASES = {
    "shodancli": ["shodan-cli"],
    "metasploit": ["msfconsole", "msfvenom"],
}


def normalize_tool_name(tool_name: str) -> str:
    """Return the canonical tool name when an alias is provided."""

    for canonical, aliases in TOOL_ALIASES.items():
        if tool_name == canonical or tool_name in aliases:
            return canonical
    return tool_name


def resolve_tool_command(tool_name: str, base_command: str) -> str:
    """
    Resolve tool command to use proper virtual environment paths for /opt tools

    Args:
        tool_name: Name of the tool
        base_command: Original command

    Returns:
        Resolved command with proper paths
    """
    canonical_tool = normalize_tool_name(tool_name)
    if canonical_tool != tool_name:
        print(f"🔁 Normalized tool name from '{tool_name}' to '{canonical_tool}'")
        if base_command.startswith(tool_name):
            normalized_command = base_command.replace(tool_name, canonical_tool, 1)
            print(f"🔁 Updated command to use canonical name: {normalized_command}")
            base_command = normalized_command

    # Check if it's one of our mapped tools
    if canonical_tool in TOOL_EXECUTABLES:
        resolved_command = TOOL_EXECUTABLES[canonical_tool]
        print(f"🔧 Resolved {canonical_tool} to: {resolved_command}")
        return resolved_command

    # Check if base_command starts with any of our tool names
    for tool, executable in TOOL_EXECUTABLES.items():
        candidate_names = [tool]
        candidate_names.extend(TOOL_ALIASES.get(tool, []))

        if any(base_command.startswith(candidate) for candidate in candidate_names):
            # Replace the tool name with the full executable path
            for candidate in candidate_names:
                if base_command.startswith(candidate):
                    resolved = base_command.replace(candidate, executable, 1)
                    print(f"🔧 Resolved command from '{base_command}' to: {resolved}")
                    return resolved

    # Return original command if no mapping found
    return base_command


# Test cases
test_cases = [
    ("prowler", "prowler aws"),
    ("kube-hunter", "kube-hunter"),
    ("scout-suite", "scout aws"),
    ("vol.py", "vol.py -f memory.dump pslist"),
    ("docker-bench-security", "docker-bench-security"),
    ("enumdns", "enumdns threat-analysis -d example.com"),
    ("stegsolve", "stegsolve"),
    ("shodancli", "shodancli host 8.8.8.8"),
    ("shodan-cli", "shodan-cli host 8.8.8.8"),
    ("metasploit", "metasploit"),
    ("msfconsole", "msfconsole"),
    ("unknown-tool", "unknown-tool --help")
]

print("🧪 Testing tool resolution functionality...")
print("=" * 60)

for tool_name, base_command in test_cases:
    print(f"\nTesting: {tool_name} | Command: {base_command}")
    resolved = resolve_tool_command(tool_name, base_command)
    print(f"Result: {resolved}")
    print("-" * 60)

print("\n✅ Tool resolution tests completed!")

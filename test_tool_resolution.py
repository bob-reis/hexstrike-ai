#!/usr/bin/env python3
"""
Test script for tool resolution functionality
"""

from tool_resolver import resolve_tool_command


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
    ("secrets_find0r", "secrets_find0r --cidr 10.0.0.0/24"),
    ("secrets_finder", "secrets_finder --cidr 10.0.0.0/24"),
    ("lfi-hunter", "lfi-hunter -UV http://example.com/vuln.php?file="),
    ("networkhound", "networkhound --dc 10.0.0.5 -d corp.local -u analyst"),
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

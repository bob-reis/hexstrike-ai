"""Utilidades compartilhadas para resolução de ferramentas externas."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


LFI_HUNTER_ROOT = Path("/opt/LFI_Hunter")
_preferred_lfi_env = LFI_HUNTER_ROOT / "lfi-hunter-venv"
if not _preferred_lfi_env.exists():
    _preferred_lfi_env = LFI_HUNTER_ROOT / "lfi-hunter-env"

_lfi_hunter_python = _preferred_lfi_env / "bin" / "python"
if _lfi_hunter_python.exists():
    LFI_HUNTER_COMMAND = (
        f"cd {LFI_HUNTER_ROOT} && {_lfi_hunter_python} "
        f"{LFI_HUNTER_ROOT / 'LFI_Hunter.py'}"
    )
else:
    LFI_HUNTER_COMMAND = ""

# Mapear ferramentas gerenciadas fora do PATH padrão.
TOOL_EXECUTABLES: Dict[str, str] = {
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
    "secrets_find0r": "/opt/secrets_find0r/secrets-env/bin/python /opt/secrets_find0r/secrets_find0r.py",
    "networkhound": "/opt/NetworkHound/networkhound-venv/bin/python /opt/NetworkHound/NetworkHound.py",
}

if LFI_HUNTER_COMMAND:
    TOOL_EXECUTABLES["lfi-hunter"] = LFI_HUNTER_COMMAND

# Aliases ajudam a detectar ferramentas cujo executável tem outro nome.
TOOL_ALIASES: Dict[str, List[str]] = {
    "ropgadget": ["ROPgadget"],
    "pwntools": ["pwn"],
    "one-gadget": ["one_gadget"],
    "volatility3": ["vol.py"],
    "vol": ["vol.py", "volatility3"],
    "volatility": ["vol", "vol.py", "volatility3"],
    "bulk-extractor": ["bulk_extractor"],
    "shodancli": ["shodan-cli"],
    "metasploit": ["msfconsole", "msfvenom"],
    "secrets_find0r": ["secrets_finder", "secretsfinder"],
    "networkhound": ["NetworkHound", "NetworkHound.py"],
}

if LFI_HUNTER_COMMAND:
    TOOL_ALIASES.setdefault("lfi-hunter", ["LFI_Hunter", "lfi_hunter", "lfi-hunter.py"])

# Caminhos alternativos usados para inferir instalação mesmo sem binários em PATH.
TOOL_INSTALLATION_HINTS: Dict[str, List[Path]] = {
    "hashcat-utils": [
        Path("/usr/lib/hashcat-utils"),
        Path("/usr/share/hashcat-utils"),
        Path("/usr/lib/hashcat-utils/cap2hccapx.bin"),
    ],
    "pwntools": [
        Path("/usr/bin/pwn"),
        Path.home() / ".local" / "bin" / "pwn",
    ],
    "one-gadget": [
        Path("/usr/local/bin/one_gadget"),
        Path("/usr/bin/one_gadget"),
        Path.home() / ".local" / "bin" / "one_gadget",
    ],
    "libc-database": [
        Path("/opt/libc-database"),
        Path.home() / "libc-database",
        Path("/usr/share/libc-database"),
    ],
    "prowler": [
        Path("/opt/prowler"),
        Path("/opt/prowler/prowler.py"),
        Path("/opt/prowler/prowlwer-venv"),
    ],
    "scout-suite": [
        Path("/opt/ScoutSuite"),
        Path("/opt/ScoutSuite/venv"),
        Path("/opt/ScoutSuite/scout.py"),
    ],
    "kube-hunter": [
        Path("/opt/kube-hunter"),
        Path("/opt/kube-hunter/venv"),
        Path("/opt/kube-hunter/kube-hunter.py"),
    ],
    "docker-bench-security": [
        Path("/opt/docker-bench-security"),
        Path("/opt/docker-bench-security/docker-bench-security.sh"),
    ],
    "volatility3": [
        Path("/opt/volatility3/vol.py"),
        Path("/opt/volatility3/volatility-env"),
    ],
    "volatility": [
        Path("/opt/volatility3/vol.py"),
        Path("/opt/volatility3/volatility-env"),
    ],
    "vol": [
        Path("/opt/volatility3/vol.py"),
        Path("/opt/volatility3/volatility-env"),
    ],
    "bulk-extractor": [
        Path("/usr/bin/bulk_extractor"),
        Path("/usr/local/bin/bulk_extractor"),
    ],
    "stegsolve": [
        Path("/opt/stegsolve/StegSolve.jar"),
        Path("/opt/stegsolve/stegsolve.jar"),
        Path("/tmp/stegsolve/StegSolve.jar"),
        Path("/tmp/stegsolve/stegsolve.jar"),
        Path("/opt/stegsolve/stegsolve"),
        Path("/opt/stegsolve"),
    ],
    "secrets_find0r": [
        Path("/opt/secrets_find0r"),
        Path("/opt/secrets_find0r/secrets-env"),
        Path("/opt/secrets_find0r/secrets_find0r.py"),
    ],
    "networkhound": [
        Path("/opt/NetworkHound"),
        Path("/opt/NetworkHound/networkhound-venv"),
        Path("/opt/NetworkHound/NetworkHound.py"),
    ],
}

if LFI_HUNTER_COMMAND:
    TOOL_INSTALLATION_HINTS.setdefault("lfi-hunter", [
        LFI_HUNTER_ROOT,
        _preferred_lfi_env,
        LFI_HUNTER_ROOT / "LFI_Hunter.py",
    ])


def normalize_tool_name(tool_name: str) -> str:
    """Retorna o nome canônico da ferramenta considerando aliases."""

    for canonical, aliases in TOOL_ALIASES.items():
        if tool_name == canonical or tool_name in aliases:
            return canonical
    return tool_name


def resolve_tool_command(tool_name: str, base_command: str) -> str:
    """Ajusta comandos para usar os binários corretos instalados em /opt."""

    canonical_tool = normalize_tool_name(tool_name)
    if canonical_tool != tool_name and base_command.startswith(tool_name):
        normalized_command = base_command.replace(tool_name, canonical_tool, 1)
        print(f"🔁 Updated command to use canonical name: {normalized_command}")
        base_command = normalized_command

    if canonical_tool in TOOL_EXECUTABLES:
        resolved_command = TOOL_EXECUTABLES[canonical_tool]
        print(f"🔧 Resolved {canonical_tool} to: {resolved_command}")
        return resolved_command

    for tool, executable in TOOL_EXECUTABLES.items():
        candidate_names = [tool]
        candidate_names.extend(TOOL_ALIASES.get(tool, []))

        for candidate in candidate_names:
            if base_command.startswith(candidate):
                resolved = base_command.replace(candidate, executable, 1)
                print(f"🔧 Resolved command from '{base_command}' to: {resolved}")
                return resolved

    return base_command


__all__ = [
    "TOOL_EXECUTABLES",
    "TOOL_ALIASES",
    "TOOL_INSTALLATION_HINTS",
    "normalize_tool_name",
    "resolve_tool_command",
]

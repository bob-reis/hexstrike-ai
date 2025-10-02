# HexStrike AI - Tool Virtual Environment Integration

## Overview

This document describes the integration of virtual environment support for security tools located in `/opt` directory. The changes ensure that Python-based security tools use their proper virtual environments and dependencies.

## Changes Made

### 1. Tool Executable Mappings

Added `TOOL_EXECUTABLES` dictionary to map tool names to their proper execution paths:

```python
TOOL_EXECUTABLES = {
    "docker-bench-security": "cd /opt/docker-bench-security && ./docker-bench-security.sh",
    "kube-hunter": "/opt/kube-hunter/venv/bin/python /opt/kube-hunter/kube-hunter.py",
    "kube-hunter-venv": "/opt/kube-hunter/venv/bin/python /opt/kube-hunter/kube-hunter.py",
    "prowler": "/opt/prowler/prowlwer-venv/bin/prowler",
    "prowler-alt": "python3 /opt/prowler/prowler.py",
    "ScoutSuite": "/opt/ScoutSuite/venv/bin/python /opt/ScoutSuite/scout.py",
    "scout-suite": "/opt/ScoutSuite/venv/bin/python /opt/ScoutSuite/scout.py",
    "volatility3": "python3 /opt/volatility3/vol.py",
    "vol.py": "python3 /opt/volatility3/vol.py",
}
```

### 2. Tool Resolution Function

Added `resolve_tool_command()` function to automatically resolve tool names to their proper execution paths:

```python
def resolve_tool_command(tool_name: str, base_command: str) -> str:
    """
    Resolve tool command to use proper virtual environment paths for /opt tools

    Args:
        tool_name: Name of the tool
        base_command: Original command

    Returns:
        Resolved command with proper paths
    """
```

### 3. Updated Tool Endpoints

Modified all relevant tool endpoints to use the resolution function:

#### Prowler (Line ~10551)
```python
base_command = f"prowler {provider}"
command = resolve_tool_command("prowler", base_command)
```

#### Kube-Hunter (Line ~10766)
```python
base_command = "kube-hunter"
command = resolve_tool_command("kube-hunter", base_command)
```

#### Docker Bench Security (Line ~10844)
```python
base_command = "docker-bench-security"
command = resolve_tool_command("docker-bench-security", base_command)
```

#### ScoutSuite (Line ~10643)
```python
base_command = f"scout {provider}"
command = resolve_tool_command("scout-suite", base_command)
```

#### Volatility3 (Line ~15306)
```python
base_command = f"vol.py -f {memory_file} {plugin}"
command = resolve_tool_command("vol.py", base_command)
```

## Tool Validation Results

### ✅ Working Tools

1. **Prowler**: Uses virtual environment at `/opt/prowler/prowlwer-venv/bin/prowler`
   - Version: 3.11.3
   - Status: Fully functional

2. **ScoutSuite**: Uses virtual environment at `/opt/ScoutSuite/venv/bin/python`
   - Status: Fully functional
   - Supports multiple cloud providers (AWS, GCP, Azure, etc.)

3. **Kube-Hunter**: Uses virtual environment at `/opt/kube-hunter/venv/bin/python`
   - Status: Fully functional
   - Requires venv for proper module resolution

4. **Volatility3**: Uses system Python at `/opt/volatility3/vol.py`
   - Status: Fully functional
   - Memory forensics tool working correctly

5. **Docker Bench Security**: Uses shell script at `/opt/docker-bench-security/`
   - Status: Functional (requires Docker daemon)
   - Needs to be executed from its directory

## File Structure

```
/opt/
├── docker-bench-security/
│   ├── docker-bench-security.sh
│   └── functions/
├── kube-hunter/
│   ├── kube-hunter.py
│   └── venv/
│       └── bin/python
├── prowler/
│   ├── prowlwer-venv/
│   │   └── bin/prowler
│   └── prowler.py
├── ScoutSuite/
│   ├── scout.py
│   └── venv/
│       └── bin/python
└── volatility3/
    └── vol.py
```

## Testing

Created `test_tool_resolution.py` to validate the resolution functionality:

```bash
python3 test_tool_resolution.py
```

All tools resolve correctly to their appropriate execution paths.

## Benefits

1. **Proper Dependencies**: Tools now use their isolated virtual environments
2. **Module Resolution**: Python tools can properly import their required modules
3. **Version Isolation**: Each tool uses its specific dependency versions
4. **Backwards Compatibility**: Original commands still work through resolution
5. **Automatic Resolution**: No manual intervention required

## Future Enhancements

1. Add more tools as they are installed in `/opt`
2. Implement automatic venv detection
3. Add health checks for tool availability
4. Monitor for tool updates and dependencies

## Notes

- All changes maintain backward compatibility
- Original tool names still work through the resolution mechanism
- Error handling preserves existing functionality
- No changes to the API interface required
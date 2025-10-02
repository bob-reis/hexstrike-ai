# EDR-Freeze Detection & Response Playbook

This playbook operationalises the Tracepoint research on the **EDR-Freeze** technique inside HexStrike. It explains how to combine the new live telemetry feed and memory-scanning workflow to detect WerFaultSecure-assisted suspensions of endpoint protection agents.

## 1. Live Telemetry Snapshot

Use the new REST endpoint or MCP tool to surface EDR-freeze heuristics in real time.

```
GET /api/processes/edr-freeze-signals?targets=MsMpEng.exe,WerFaultSecure.exe
```

HexStrike MCP tool:

- `detect_edr_freeze_signals(targets="MsMpEng.exe,WerFaultSecure.exe", include_snapshot=False)`

Key fields returned:

- `helper_processes`: WerFaultSecure / WerFault helpers with CLI flags, open-file hits, and handle counts.
- `suspicious_targets`: Defender or monitored processes showing stopped threads / status.
- `artifact_hits`: File paths matching `t.txt` or `dump_<pid>.txt` artefacts observed during the freeze window.
- `correlations`: Helper → target pairings (parsed from `/pid` `/tid` arguments) with match confidence.
- `analysis_notes`: High-level summary of observed indicators.

Enable `include_snapshot=true` when you need the complete per-process breakdown (thread states, cmdlines, open files). This snapshot is useful for timeline reconstruction but may be large, so keep it disabled for routine polling.

### Recommended Workflow

1. Poll the endpoint when suspicious telemetry spikes occur or during scheduled health checks.
2. Focus on entries where `analysis_notes` mention correlated helper/target pairs or suspended threads.
3. Preserve any files listed in `artifact_hits` before an attacker deletes them (`t.txt`, `dump_*.txt`).

## 2. Memory Validation with YARA

Corroborate live telemetry by scanning a captured memory snapshot using the bundled rule sets.

```
POST /api/forensics/edr-freeze-scan
{
  "memory_file": "/mnt/dumps/win11defender.raw",
  "yara_file": "/mnt/rules/CAP_WerFaultSecure_Freeze_Technique_v2.yar",
  "additional_args": "--pid 10892"
}
```

HexStrike MCP tool:

- `run_edr_freeze_yara_scan(memory_file, yara_file, plugin="", profile="", additional_args="--pid 10892")`

Output highlights:

- `match_count` and `matches` – raw lines emitted by Volatility's `VadYaraScan` plugin.
- `analysis_notes` – quick interpretation (e.g., WerFaultSecure hits, Defender artefacts, transient `t.txt`).
- `command` – exact command executed via the `/opt/volatility3` wrapper for audit trails.

The endpoint defaults to `windows.vadyarascan.VadYaraScan`; override `plugin` or `profile` if the target image needs custom handling. Set `include_matches=false` to save bandwidth when only the summary matters.

## 3. Investigation & Response Checklist

1. **Capture Telemetry:** Run `detect_edr_freeze_signals` with monitored process names (`MsMpEng.exe`, `SenseIR.exe`) while the incident is active.
2. **Confirm Suspension:** Look for `suspended_threads` and `Process status reports stopped/tracing state` within the `suspicious_targets` array.
3. **Correlate Helpers:** Validate that `correlations` map WerFaultSecure → Defender with high confidence and note `/pid` `/tid` arguments for the timeline.
4. **Preserve Artefacts:** Quarantine file paths listed in `artifact_hits`; they explain temporary dump handles created by the PoC.
5. **Scan Memory:** Execute `run_edr_freeze_yara_scan` against RAM acquisitions using the CAP/BEHAVIOR rulesets from Tracepoint. Review `analysis_notes` for final confirmation.
6. **Hunt Laterally:** Re-run the telemetry snapshot across other hosts or time windows to catch repeated use of the technique.

## 4. Integration Tips

- Chain `/api/processes/edr-freeze-signals` results into existing health dashboards; the response includes `system_metrics` alongside freeze-specific findings.
- Export `analysis_notes` and `correlations` directly into case-management tickets to shorten analyst hand-offs.
- Feed `matches` from the YARA scan into your incident repository; they already surface `WerFaultSecure` and `MsMpEng` references for IOC sharing.
- Pair the telemetry snapshot with EnumDNS → httpx/nuclei workflows when suspicious helper processes touch remote infrastructure, keeping investigation data consolidated.

These additions let HexStrike detect, validate, and document EDR-Freezing behaviour without waiting for external tooling, aligning our controls with the Tracepoint guidance.


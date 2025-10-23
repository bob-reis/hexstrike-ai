"""Static scanner para primitivas de desserializacao inseguras."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

SKIP_PARTS = {".git", "__pycache__", "hexstrike-env", ".venv", "venv", "env"}

UNSAFE_CALLS = {
    "pickle.load",
    "pickle.loads",
    "cloudpickle.load",
    "cloudpickle.loads",
    "torch.load",
    "torch.serialization.load",
}

SAFE_TORCH_KW = "weights_only"


@dataclass
class Issue:
    path: str
    line: int
    call: str
    severity: str
    message: str
    recommendation: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "call": self.call,
            "severity": self.severity,
            "message": self.message,
            "recommendation": self.recommendation,
        }


class ImportResolver(ast.NodeVisitor):
    """Mapeia aliases de importacao para resolucao posterior."""

    def __init__(self) -> None:
        self.aliases: Dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            target = alias.name
            asname = alias.asname or target
            self.aliases[asname] = target
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            target = f"{module}.{alias.name}" if module else alias.name
            asname = alias.asname or alias.name
            self.aliases[asname] = target
        self.generic_visit(node)


def _resolve_call_name(func: ast.AST, aliases: Dict[str, str]) -> Optional[str]:
    if isinstance(func, ast.Name):
        return aliases.get(func.id, func.id)
    if isinstance(func, ast.Attribute):
        base = _resolve_call_name(func.value, aliases)
        if not base:
            return None
        return f"{base}.{func.attr}"
    return None


class PickleUsageVisitor(ast.NodeVisitor):
    def __init__(self, aliases: Dict[str, str]) -> None:
        self.aliases = aliases
        self.issues: List[Issue] = []

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _resolve_call_name(node.func, self.aliases)
        if call_name:
            simplified = call_name
            if simplified.startswith("torch.serialization.load"):
                simplified = "torch.serialization.load"
            elif simplified.startswith("torch.load"):
                simplified = "torch.load"

            if simplified in UNSAFE_CALLS:
                if simplified.startswith("torch"):
                    has_safe_kw = any(
                        kw.arg == SAFE_TORCH_KW
                        and isinstance(kw.value, ast.Constant)
                        and bool(kw.value.value)
                        for kw in node.keywords
                    )
                    if not has_safe_kw:
                        self.issues.append(
                            Issue(
                                path="",
                                line=node.lineno,
                                call=simplified,
                                severity="medium",
                                message="torch.load chamado sem weights_only=True",
                                recommendation="Use torch.load(weights_only=True) ou formatos como safetensors/ONNX",
                            )
                        )
                else:
                    self.issues.append(
                        Issue(
                            path="",
                            line=node.lineno,
                            call=simplified,
                            severity="high",
                            message=f"Primitiva de desserializacao insegura detectada: {simplified}",
                            recommendation="Substitua por loader seguro ou valide a procedencia do pickle",
                        )
                    )
        self.generic_visit(node)


def _materialise_candidates(root: Path) -> Sequence[Path]:
    if root.is_file():
        return [root]
    candidates: List[Path] = []
    for py_file in root.rglob("*.py"):
        if any(part in SKIP_PARTS for part in py_file.parts):
            continue
        candidates.append(py_file)
    return candidates


def scan_python_path(path: Path) -> Dict[str, object]:
    root = path.resolve()
    if root.is_file() and root.suffix != ".py":
        raise ValueError("scan_python_path espera diretorio ou arquivo .py")

    candidates = _materialise_candidates(root)
    base = root if root.is_dir() else root.parent

    issues: List[Dict[str, object]] = []
    issue_files: Set[str] = set()

    for file_path in candidates:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            continue

        resolver = ImportResolver()
        resolver.visit(tree)
        visitor = PickleUsageVisitor(resolver.aliases)
        visitor.visit(tree)

        rel_path = str(file_path.relative_to(base))
        for issue in visitor.issues:
            issue.path = rel_path
            issues.append(issue.to_dict())
            issue_files.add(rel_path)

    total_files = len(candidates)
    safe_files = total_files - len(issue_files)

    return {
        "root": str(root),
        "issues": issues,
        "summary": {
            "total_files": total_files,
            "files_with_findings": len(issue_files),
            "high_findings": sum(1 for item in issues if item["severity"] == "high"),
            "medium_findings": sum(1 for item in issues if item["severity"] == "medium"),
            "safe_files": safe_files,
        },
        "recommendations": [
            "Trate checkpoints/modelos como entrada nao confiavel.",
            "Prefira safetensors, ONNX ou loaders com weights_only.",
            "Assine e verifique artefatos de modelo.",
        ],
    }


def scan(path: str) -> Dict[str, object]:
    return scan_python_path(Path(path))


__all__ = ["scan", "scan_python_path", "Issue"]


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Detecta uso inseguro de pickle/torch load")
    parser.add_argument("path", help="Diretorio ou arquivo para analise", default=".")
    args = parser.parse_args()
    result = scan(args.path)
    print(json.dumps(result, indent=2))

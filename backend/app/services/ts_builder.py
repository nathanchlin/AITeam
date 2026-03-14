from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TSCommandResult:
    passed: bool
    command: List[str]
    stdout: str
    stderr: str
    returncode: int
    errors: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class TSBuilder:
    """Build and validate generated Vite + TypeScript projects."""

    def __init__(self):
        self.npm_path = shutil.which("npm")

    def _missing_npm_result(self) -> TSCommandResult:
        return TSCommandResult(
            passed=False,
            command=[],
            stdout="",
            stderr="npm not found",
            returncode=127,
            errors=["未找到 npm，无法构建 TypeScript 工程"],
            warnings=[],
        )

    def _run(self, command: List[str], cwd: str, timeout: int = 300) -> TSCommandResult:
        if not self.npm_path:
            return self._missing_npm_result()

        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return TSCommandResult(
                passed=False,
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                returncode=124,
                errors=[f"命令执行超时（{timeout} 秒）：{' '.join(command)}"],
                warnings=[],
            )
        except Exception as exc:
            return TSCommandResult(
                passed=False,
                command=command,
                stdout="",
                stderr=str(exc),
                returncode=1,
                errors=[f"命令执行失败：{exc}"],
                warnings=[],
            )

        combined = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part).strip()
        errors: List[str] = []
        warnings: List[str] = []

        if completed.returncode != 0:
            lines = [line.strip() for line in combined.splitlines() if line.strip()]
            errors = lines[:20] if lines else [f"命令执行失败：{' '.join(command)}"]
        elif combined:
            warnings = [line.strip() for line in combined.splitlines() if line.strip()][:10]

        return TSCommandResult(
            passed=completed.returncode == 0,
            command=command,
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            errors=errors,
            warnings=warnings,
        )

    def ensure_dependencies(self, project_dir: str) -> TSCommandResult:
        project_path = Path(project_dir)
        node_modules = project_path / "node_modules"

        if node_modules.exists():
            return TSCommandResult(
                passed=True,
                command=[self.npm_path or "npm", "install"],
                stdout="node_modules already exists",
                stderr="",
                returncode=0,
                errors=[],
                warnings=[],
            )

        return self._run(
            [self.npm_path or "npm", "install", "--no-fund", "--no-audit"],
            cwd=str(project_path),
            timeout=600,
        )

    def compile_check(self, project_dir: str) -> TSCommandResult:
        deps_result = self.ensure_dependencies(project_dir)
        if not deps_result.passed:
            return deps_result

        typecheck_result = self._run(
            [self.npm_path or "npm", "run", "typecheck"],
            cwd=project_dir,
            timeout=240,
        )
        if not typecheck_result.passed:
            return typecheck_result

        bundle_dir = Path(project_dir) / ".tsbuild-check"
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir, ignore_errors=True)

        bundle_result = self._run(
            [self.npm_path or "npm", "run", "bundle-check"],
            cwd=project_dir,
            timeout=240,
        )

        if bundle_dir.exists():
            shutil.rmtree(bundle_dir, ignore_errors=True)

        return bundle_result

    def build(self, project_dir: str) -> TSCommandResult:
        deps_result = self.ensure_dependencies(project_dir)
        if not deps_result.passed:
            return deps_result

        build_result = self._run(
            [self.npm_path or "npm", "run", "build"],
            cwd=project_dir,
            timeout=600,
        )
        dist_index = Path(project_dir) / "dist" / "index.html"
        if build_result.passed and not dist_index.exists():
            return TSCommandResult(
                passed=False,
                command=build_result.command,
                stdout=build_result.stdout,
                stderr=build_result.stderr,
                returncode=build_result.returncode,
                errors=["构建命令已完成，但 dist/index.html 未生成"],
                warnings=build_result.warnings,
            )
        return build_result


ts_builder = TSBuilder()

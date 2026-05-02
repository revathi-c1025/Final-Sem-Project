from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .models import ExecutionResult


class ExecutionEngine:
    def __init__(self, output_dir: str = "generated_tests") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, code: str) -> ExecutionResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        test_file = self.output_dir / f"test_generated_{timestamp}.py"
        test_file.write_text(code, encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        logs = completed.stdout.strip()
        errors = completed.stderr.strip()
        status = "success" if completed.returncode == 0 else "failure"
        return ExecutionResult(
            status=status,
            logs=logs,
            errors=errors,
            return_code=completed.returncode,
            test_file=str(test_file),
        )

"""
Test Executor Agent - Runs generated test scripts, captures all output and logs.
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from config import TEST_TIMEOUT_SECONDS, LOGS_DIR


class ExecutionResult:
    """Holds the complete result of a test execution."""

    def __init__(self, test_case_id, file_path, attempt):
        self.test_case_id = test_case_id
        self.file_path = file_path
        self.attempt = attempt
        self.return_code = None
        self.stdout = ""
        self.stderr = ""
        self.duration_seconds = 0
        self.status = "not_run"  # passed, failed, error, timeout
        self.error_type = ""
        self.error_message = ""
        self.traceback = ""
        self.timestamp = datetime.now().isoformat()
        self.log_file = ""
        self.junit_xml = ""

    @property
    def success(self):
        return self.status == "passed"

    def to_dict(self):
        return {
            "test_case_id": self.test_case_id,
            "file_path": self.file_path,
            "attempt": self.attempt,
            "return_code": self.return_code,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "traceback": self.traceback[:2000],
            "timestamp": self.timestamp,
            "log_file": self.log_file,
            "stdout_tail": self.stdout[-1000:] if self.stdout else "",
            "stderr_tail": self.stderr[-1000:] if self.stderr else "",
        }

    def get_error_info(self):
        """Get error info dict suitable for the FixerAgent/TestGeneratorAgent."""
        return {
            "return_code": self.return_code,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "traceback": self.traceback,
            "stderr": self.stderr,
            "stdout": self.stdout,
        }


class TestExecutorAgent(BaseAgent):
    """
    Agent that executes generated Python test scripts via pytest.
    Captures stdout, stderr, log files, and parses results.
    """

    def __init__(self):
        super().__init__("TestExecutorAgent")
        self.execution_history = []
        self.log_event("init", "TestExecutorAgent initialized.")

    def execute_test(self, file_path, test_case_id, attempt=1, extra_env=None):
        """
        Execute a generated test file using pytest.

        Args:
            file_path: Path to the test .py file
            test_case_id: qTest test case PID (e.g. TC-174995)
            attempt: Attempt number (1-based)
            extra_env: Optional dict of additional environment variables

        Returns:
            ExecutionResult object
        """
        self.start_timer()
        result = ExecutionResult(test_case_id, file_path, attempt)

        self.log_event("execute_start",
                        f"Executing {test_case_id} (attempt {attempt}): {os.path.basename(file_path)}")

        # Prepare log directory
        os.makedirs(LOGS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(LOGS_DIR,
                                 f"{test_case_id}_attempt{attempt}_{timestamp}.log")
        junit_xml = os.path.join(LOGS_DIR,
                                  f"{test_case_id}_attempt{attempt}_{timestamp}_junit.xml")
        result.log_file = log_file
        result.junit_xml = junit_xml

        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            file_path,
            "-v",
            "--tb=long",
            f"--log-file={log_file}",
            "--log-file-level=DEBUG",
            "--log-cli-level=INFO",
            f"--junitxml={junit_xml}",
            "-s",  # capture output
        ]

        # Build environment
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        # Execute
        start_time = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT_SECONDS,
                env=env,
                cwd=os.path.dirname(file_path),
            )
            result.return_code = proc.returncode
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.duration_seconds = round(time.time() - start_time, 2)

            if proc.returncode == 0:
                result.status = "passed"
            else:
                result.status = "failed"
                self._parse_error(result)

        except subprocess.TimeoutExpired as e:
            result.status = "timeout"
            result.duration_seconds = TEST_TIMEOUT_SECONDS
            result.error_type = "TimeoutError"
            result.error_message = f"Test exceeded {TEST_TIMEOUT_SECONDS}s timeout"
            result.stdout = e.stdout or ""
            result.stderr = e.stderr or ""

        except Exception as e:
            result.status = "error"
            result.duration_seconds = round(time.time() - start_time, 2)
            result.error_type = type(e).__name__
            result.error_message = str(e)

        # Save execution log
        self._save_execution_log(result, log_file)

        self.execution_history.append(result)

        self.log_event("execute_complete",
                        f"{test_case_id} attempt {attempt}: {result.status} "
                        f"(rc={result.return_code}, {result.duration_seconds}s)",
                        result.to_dict())

        return result

    def _parse_error(self, result):
        """Parse error details from pytest output."""
        output = result.stdout + "\n" + result.stderr

        # Extract traceback
        tb_lines = []
        in_traceback = False
        for line in output.split('\n'):
            if 'Traceback (most recent call last)' in line or 'FAILED' in line:
                in_traceback = True
            if in_traceback:
                tb_lines.append(line)
            if in_traceback and (line.strip().startswith('E ') or
                                  line.strip().startswith('>')):
                pass  # continue collecting

        result.traceback = '\n'.join(tb_lines[-50:])  # Last 50 lines

        # Identify error type
        error_patterns = [
            (r'(\w+Error): (.+)', 'error'),
            (r'(\w+Exception): (.+)', 'exception'),
            (r'FAILED .+ - (\w+): (.+)', 'assertion'),
            (r'E\s+(\w+Error):\s+(.+)', 'pytest_error'),
            (r'E\s+(\w+Exception):\s+(.+)', 'pytest_exception'),
        ]

        import re
        for pattern, _ in error_patterns:
            match = re.search(pattern, output)
            if match:
                result.error_type = match.group(1)
                result.error_message = match.group(2)[:500]
                break

        if not result.error_type:
            result.error_type = "UnknownError"
            result.error_message = "Test failed - see logs for details"

    def _save_execution_log(self, result, log_file):
        """Append execution metadata to the log file."""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("EXECUTION METADATA\n")
                f.write("=" * 60 + "\n")
                f.write(json.dumps(result.to_dict(), indent=2, default=str))
                f.write("\n\n--- STDOUT ---\n")
                f.write(result.stdout or "(empty)")
                f.write("\n\n--- STDERR ---\n")
                f.write(result.stderr or "(empty)")
        except Exception:
            pass

    def get_execution_summary(self):
        """Get a summary of all executions."""
        total = len(self.execution_history)
        passed = sum(1 for r in self.execution_history if r.success)
        failed = sum(1 for r in self.execution_history if r.status == "failed")
        errors = sum(1 for r in self.execution_history if r.status == "error")
        timeouts = sum(1 for r in self.execution_history if r.status == "timeout")
        return {
            "total_executions": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "timeouts": timeouts,
            "executions": [r.to_dict() for r in self.execution_history],
        }

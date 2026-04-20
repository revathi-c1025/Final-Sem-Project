"""
Fixer Agent - Analyzes test failures and determines fix strategies.
Works with TestGeneratorAgent to produce corrected test code.
"""

import re
from agents.base_agent import BaseAgent


class FixStrategy:
    """Represents a fix strategy for a test failure."""

    def __init__(self, strategy_type, description, confidence, details=None):
        self.strategy_type = strategy_type
        self.description = description
        self.confidence = confidence  # 0.0 - 1.0
        self.details = details or {}

    def to_dict(self):
        return {
            "strategy": self.strategy_type,
            "description": self.description,
            "confidence": self.confidence,
            "details": self.details,
        }


class FixerAgent(BaseAgent):
    """
    Agent that analyzes test execution failures and determines fix strategies.
    It classifies errors and provides context for the TestGeneratorAgent to regenerate.
    """

    def __init__(self):
        super().__init__("FixerAgent")
        self.fix_history = []
        self.log_event("init", "FixerAgent initialized.")

    def analyze_failure(self, execution_result):
        """
        Analyze a failed test execution and produce fix strategies.

        Args:
            execution_result: ExecutionResult from TestExecutorAgent

        Returns:
            list[FixStrategy]: Ordered list of fix strategies to try
        """
        self.start_timer()
        self.log_event("analyze_start",
                        f"Analyzing failure for {execution_result.test_case_id} "
                        f"(attempt {execution_result.attempt})")

        error_info = execution_result.get_error_info()
        strategies = []

        # Classify the error
        error_class = self._classify_error(error_info)
        self.log_event("error_classified", f"Error class: {error_class}",
                        {"error_type": error_info.get("error_type"),
                         "error_class": error_class})

        # Generate strategies based on error class
        if error_class == "import_error":
            strategies.append(FixStrategy(
                "add_missing_import",
                "Add missing import statement",
                0.9,
                self._extract_missing_import(error_info)
            ))

        elif error_class == "connection_error":
            strategies.extend([
                FixStrategy(
                    "add_timeout_retry",
                    "Add timeout and retry logic for network calls",
                    0.8,
                    {"timeout": 30, "retries": 3}
                ),
                FixStrategy(
                    "skip_if_unreachable",
                    "Mark API-dependent steps as skippable when ShopEasy API is unreachable",
                    0.7,
                ),
            ])

        elif error_class == "ssl_error":
            strategies.append(FixStrategy(
                "disable_ssl_verify",
                "Add SSL verification bypass",
                0.9,
            ))

        elif error_class == "auth_error":
            strategies.extend([
                FixStrategy(
                    "fix_auth_flow",
                    "Fix authentication flow (headers, credentials)",
                    0.7,
                ),
                FixStrategy(
                    "skip_if_no_auth",
                    "Skip auth-dependent tests when credentials not available",
                    0.6,
                ),
            ])

        elif error_class == "assertion_error":
            strategies.extend([
                FixStrategy(
                    "fix_assertion",
                    "Fix assertion logic based on actual vs expected values",
                    0.7,
                    self._extract_assertion_details(error_info)
                ),
                FixStrategy(
                    "soften_assertion",
                    "Convert hard assertion to soft check with logging",
                    0.5,
                ),
            ])

        elif error_class == "timeout_error":
            strategies.append(FixStrategy(
                "increase_timeout",
                "Increase test timeout and add wait logic",
                0.8,
                {"new_timeout": 600}
            ))

        elif error_class == "syntax_error":
            strategies.append(FixStrategy(
                "fix_syntax",
                "Fix Python syntax error in generated code",
                0.9,
                self._extract_syntax_error_details(error_info)
            ))

        elif error_class == "attribute_error":
            strategies.append(FixStrategy(
                "fix_attribute_access",
                "Fix attribute/key access pattern",
                0.8,
                self._extract_attribute_details(error_info)
            ))

        else:
            strategies.append(FixStrategy(
                "regenerate_full",
                "Full regeneration with error context provided to LLM/template",
                0.5,
            ))

        # Always add full regeneration as last resort
        if not any(s.strategy_type == "regenerate_full" for s in strategies):
            strategies.append(FixStrategy(
                "regenerate_full",
                "Full regeneration as fallback",
                0.3,
            ))

        fix_record = {
            "test_case_id": execution_result.test_case_id,
            "attempt": execution_result.attempt,
            "error_class": error_class,
            "strategies": [s.to_dict() for s in strategies],
            "elapsed_s": self.elapsed_seconds(),
        }
        self.fix_history.append(fix_record)

        self.log_event("analyze_complete",
                        f"Found {len(strategies)} fix strategies for {error_class}",
                        fix_record)

        return strategies

    def should_retry(self, execution_result, max_retries):
        """Determine if we should retry based on the failure type."""
        if execution_result.success:
            return False
        if execution_result.attempt >= max_retries:
            self.log_event("retry_limit", f"Max retries ({max_retries}) reached")
            return False
        error_class = self._classify_error(execution_result.get_error_info())
        # Don't retry for certain unrecoverable errors
        if error_class in ("syntax_error",):
            return True  # Syntax errors are fixable
        if error_class == "connection_error" and execution_result.attempt >= 2:
            self.log_event("retry_skip", "Connection error persists after 2 attempts, skipping")
            return False
        return True

    def _classify_error(self, error_info):
        """Classify the error into a category."""
        error_type = error_info.get("error_type", "")
        error_msg = error_info.get("error_message", "")
        traceback = error_info.get("traceback", "")
        stderr = error_info.get("stderr", "")
        combined = f"{error_type} {error_msg} {traceback} {stderr}"

        if "ModuleNotFoundError" in combined or "ImportError" in combined:
            return "import_error"
        if "SyntaxError" in combined or "IndentationError" in combined:
            return "syntax_error"
        if "ConnectionError" in combined or "ConnectTimeout" in combined or "ConnectionRefused" in combined:
            return "connection_error"
        if "SSLError" in combined or "CERTIFICATE_VERIFY_FAILED" in combined:
            return "ssl_error"
        if "401" in combined or "403" in combined or "Unauthorized" in combined:
            return "auth_error"
        if "AssertionError" in combined or "assert" in combined.lower():
            return "assertion_error"
        if "TimeoutError" in combined or "timeout" in error_type.lower():
            return "timeout_error"
        if "AttributeError" in combined or "KeyError" in combined:
            return "attribute_error"
        if "TypeError" in combined:
            return "type_error"
        return "unknown_error"

    def _extract_missing_import(self, error_info):
        """Extract the missing module name from import error."""
        combined = error_info.get("traceback", "") + error_info.get("stderr", "")
        match = re.search(r"No module named '([^']+)'", combined)
        if match:
            return {"missing_module": match.group(1)}
        return {}

    def _extract_assertion_details(self, error_info):
        """Extract assertion details (expected vs actual)."""
        combined = error_info.get("traceback", "")
        details = {}
        match = re.search(r"assert\s+(.+?)\s*==\s*(.+)", combined)
        if match:
            details["actual"] = match.group(1).strip()
            details["expected"] = match.group(2).strip()
        return details

    def _extract_syntax_error_details(self, error_info):
        """Extract syntax error location details."""
        combined = error_info.get("stderr", "") + error_info.get("traceback", "")
        details = {}
        match = re.search(r'File "([^"]+)", line (\d+)', combined)
        if match:
            details["file"] = match.group(1)
            details["line"] = int(match.group(2))
        match = re.search(r"SyntaxError: (.+)", combined)
        if match:
            details["message"] = match.group(1)
        return details

    def _extract_attribute_details(self, error_info):
        """Extract attribute error details."""
        combined = error_info.get("traceback", "")
        details = {}
        match = re.search(r"AttributeError: '(\w+)' object has no attribute '(\w+)'", combined)
        if match:
            details["object_type"] = match.group(1)
            details["missing_attr"] = match.group(2)
        match = re.search(r"KeyError: '([^']+)'", combined)
        if match:
            details["missing_key"] = match.group(1)
        return details

    def get_fix_summary(self):
        """Get summary of all fix analyses."""
        return {
            "total_analyses": len(self.fix_history),
            "analyses": self.fix_history,
        }

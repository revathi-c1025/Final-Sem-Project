"""
Orchestrator Agent - Coordinates all agents in the test automation pipeline.
Manages the full lifecycle: fetch -> generate -> execute -> fix -> retry -> report.
"""

import os
import json
import time
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.qtest_agent import QTestAgent
# from agents.test_generator_agent import TestGeneratorAgent  # Temporarily disabled
from simple_test_generator import SimpleTestGenerator  # Using simple generator
from agents.test_executor_agent import TestExecutorAgent
from agents.fixer_agent import FixerAgent
from config import MAX_RETRIES, RETRY_DELAY_SECONDS, REPORTS_DIR, LOGS_DIR


class TestCycleResult:
    """Holds the complete lifecycle result for a single test case."""

    def __init__(self, test_case_id):
        self.test_case_id = test_case_id
        self.test_case_data = None
        self.generated_tests = []
        self.execution_results = []
        self.fix_strategies = []
        self.final_status = "not_run"
        self.total_attempts = 0
        self.start_time = datetime.now().isoformat()
        self.end_time = None
        self.duration_seconds = 0

    def to_dict(self):
        return {
            "test_case_id": self.test_case_id,
            "test_case_name": (self.test_case_data or {}).get("name", ""),
            "final_status": self.final_status,
            "total_attempts": self.total_attempts,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "step_count": (self.test_case_data or {}).get("step_count", 0),
            "generated_tests": [
                {"file": g.get("file_path", ""), "method": g.get("method", "")}
                for g in self.generated_tests
            ],
            "execution_results": [e.to_dict() for e in self.execution_results],
            "fix_strategies": self.fix_strategies,
        }


class OrchestratorAgent(BaseAgent):
    """
    Master agent that orchestrates the complete test automation pipeline:
    1. Fetch test case from test management system (QTestAgent / demo JSON)
    2. Generate executable test code (TestGeneratorAgent)
    3. Execute the test (TestExecutorAgent)
    4. On failure: analyze and fix (FixerAgent + TestGeneratorAgent)
    5. Retry with fixed code (up to MAX_RETRIES)
    6. Produce comprehensive report
    """

    def __init__(self, enable_rag=True):
        super().__init__("OrchestratorAgent")
        self.qtest_agent = QTestAgent()

        # Initialize RAG system if enabled
        self.rag_system = None
        if enable_rag:
            try:
                from rag_system import get_rag_system, initialize_rag_with_sample_data
                self.rag_system = get_rag_system()
                initialize_rag_with_sample_data()
                self.log_event("rag_init", "RAG system initialized successfully")
            except Exception as e:
                self.log_event("rag_init_fail", f"RAG system initialization failed: {e}")
                self.rag_system = None

        # Initialize generator with RAG system
        self.generator_agent = SimpleTestGenerator(rag_system=self.rag_system)
        self.executor_agent = TestExecutorAgent()
        self.fixer_agent = FixerAgent()
        self.cycle_results = []
        self.log_event("init", "OrchestratorAgent initialized with all sub-agents.")

    def run_test_case(self, test_case_id, extra_env=None):
        """
        Run the full automation cycle for a single test case.

        Args:
            test_case_id: Test case PID (e.g., "TC-001") or numeric ID
            extra_env: Optional dict of environment variables for test execution

        Returns:
            TestCycleResult
        """
        cycle = TestCycleResult(test_case_id)
        pipeline_start = time.time()

        self.log_event("pipeline_start", f"Starting pipeline for {test_case_id}")

        # =====================================================================
        # Phase 1: Fetch test case
        # =====================================================================
        self.log_event("phase", "Phase 1: Fetching test case")
        try:
            tc_data = self.qtest_agent.fetch_test_case(test_case_id)
            cycle.test_case_data = tc_data
            self.log_event("fetch_ok",
                            f"Fetched {tc_data['pid']}: {tc_data['name'][:60]} "
                            f"({tc_data['step_count']} steps)")
        except Exception as e:
            self.log_event("fetch_fail", f"Failed to fetch test case: {e}")
            cycle.final_status = "fetch_failed"
            cycle.end_time = datetime.now().isoformat()
            cycle.duration_seconds = round(time.time() - pipeline_start, 2)
            self.cycle_results.append(cycle)
            return cycle

        if tc_data["step_count"] == 0:
            self.log_event("no_steps", f"Test case {test_case_id} has no steps")
            cycle.final_status = "no_steps"
            cycle.end_time = datetime.now().isoformat()
            cycle.duration_seconds = round(time.time() - pipeline_start, 2)
            self.cycle_results.append(cycle)
            return cycle

        # =====================================================================
        # Phase 2: Generate initial test code
        # =====================================================================
        self.log_event("phase", "Phase 2: Generating test code")
        try:
            gen_result = self.generator_agent.generate_test(tc_data)
            cycle.generated_tests.append(gen_result)
            self.log_event("generate_ok",
                            f"Generated {gen_result['method']} test: "
                            f"{os.path.basename(gen_result['file_path'])}")
        except Exception as e:
            self.log_event("generate_fail", f"Failed to generate test: {e}")
            cycle.final_status = "generation_failed"
            cycle.end_time = datetime.now().isoformat()
            cycle.duration_seconds = round(time.time() - pipeline_start, 2)
            self.cycle_results.append(cycle)
            return cycle

        # =====================================================================
        # Phase 3: Execute + Fix + Retry loop
        # =====================================================================
        current_code = gen_result["code"]
        current_file = gen_result["file_path"]
        attempt = 0

        while attempt < MAX_RETRIES:
            attempt += 1
            cycle.total_attempts = attempt

            self.log_event("phase",
                            f"Phase 3: Execution attempt {attempt}/{MAX_RETRIES}")

            # Execute
            exec_result = self.executor_agent.execute_test(
                current_file, test_case_id, attempt=attempt, extra_env=extra_env)
            cycle.execution_results.append(exec_result)

            if exec_result.success:
                self.log_event("test_passed",
                                f"{test_case_id} PASSED on attempt {attempt} "
                                f"({exec_result.duration_seconds}s)")
                cycle.final_status = "passed"
                break

            self.log_event("test_failed",
                            f"{test_case_id} FAILED on attempt {attempt}: "
                            f"{exec_result.error_type}: {exec_result.error_message[:100]}")

            # Check if we should retry
            if not self.fixer_agent.should_retry(exec_result, MAX_RETRIES):
                self.log_event("no_retry", "Fixer determined no retry needed")
                cycle.final_status = "failed"
                break

            # Analyze failure and get fix strategies
            strategies = self.fixer_agent.analyze_failure(exec_result)
            cycle.fix_strategies.extend([s.to_dict() for s in strategies])

            if attempt < MAX_RETRIES:
                self.log_event("phase",
                                f"Phase 4: Regenerating test (fix attempt {attempt})")

                # Delay before retry
                time.sleep(RETRY_DELAY_SECONDS)

                # Regenerate test with error context
                try:
                    regen_result = self.generator_agent.regenerate_test(
                        tc_data, current_code, exec_result.get_error_info())
                    cycle.generated_tests.append(regen_result)
                    current_code = regen_result["code"]
                    current_file = regen_result["file_path"]
                    self.log_event("regenerate_ok",
                                    f"Regenerated test: {os.path.basename(current_file)}")
                except Exception as e:
                    self.log_event("regenerate_fail", f"Failed to regenerate: {e}")
                    cycle.final_status = "fix_failed"
                    break
        else:
            cycle.final_status = "failed"

        # =====================================================================
        # Phase 5: Finalize
        # =====================================================================
        cycle.end_time = datetime.now().isoformat()
        cycle.duration_seconds = round(time.time() - pipeline_start, 2)

        self.log_event("pipeline_complete",
                        f"Pipeline for {test_case_id}: {cycle.final_status} "
                        f"({cycle.total_attempts} attempts, {cycle.duration_seconds}s)")

        self.cycle_results.append(cycle)
        return cycle

    def run_batch(self, test_case_ids, extra_env=None):
        """
        Run the pipeline for multiple test cases.

        Args:
            test_case_ids: List of test case PIDs
            extra_env: Optional environment dict

        Returns:
            list[TestCycleResult]
        """
        self.log_event("batch_start", f"Starting batch of {len(test_case_ids)} test cases")
        results = []

        for i, tc_id in enumerate(test_case_ids, 1):
            self.log_event("batch_progress", f"Processing {i}/{len(test_case_ids)}: {tc_id}")
            result = self.run_test_case(tc_id, extra_env=extra_env)
            results.append(result)

        self.log_event("batch_complete",
                        f"Batch complete: {len(results)} test cases processed")
        return results

    def generate_report(self, cycle_results=None):
        """
        Generate a comprehensive JSON + HTML report of all pipeline runs.

        Args:
            cycle_results: Optional list of TestCycleResult; defaults to self.cycle_results

        Returns:
            dict with report file paths
        """
        results = cycle_results or self.cycle_results
        os.makedirs(REPORTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # ---- JSON Report ----
        report_data = {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_test_cases": len(results),
                "passed": sum(1 for r in results if r.final_status == "passed"),
                "failed": sum(1 for r in results if r.final_status == "failed"),
                "other": sum(1 for r in results if r.final_status not in ("passed", "failed")),
                "total_attempts": sum(r.total_attempts for r in results),
                "total_duration_s": sum(r.duration_seconds for r in results),
            },
            "test_cases": [r.to_dict() for r in results],
            "agent_events": {
                "orchestrator": self.get_events(),
                "qtest": self.qtest_agent.get_events(),
                "generator": self.generator_agent.get_events(),
                "executor": self.executor_agent.get_events(),
                "fixer": self.fixer_agent.get_events(),
            },
            "execution_summary": self.executor_agent.get_execution_summary(),
            "fix_summary": self.fixer_agent.get_fix_summary(),
        }

        json_path = os.path.join(REPORTS_DIR, f"report_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, default=str)

        # ---- HTML Report ----
        html_path = os.path.join(REPORTS_DIR, f"report_{timestamp}.html")
        self._write_html_report(html_path, report_data)

        self.log_event("report_generated",
                        f"Reports saved: {json_path}, {html_path}")

        return {"json": json_path, "html": html_path, "data": report_data}

    def _write_html_report(self, html_path, data):
        """Generate an HTML report."""
        summary = data["summary"]
        tc_rows = ""
        for tc in data["test_cases"]:
            status_class = "pass" if tc["final_status"] == "passed" else "fail"
            tc_rows += f"""
            <tr class="{status_class}">
                <td>{tc['test_case_id']}</td>
                <td>{tc['test_case_name'][:60]}</td>
                <td><strong>{tc['final_status'].upper()}</strong></td>
                <td>{tc['total_attempts']}</td>
                <td>{tc['step_count']}</td>
                <td>{tc['duration_seconds']}s</td>
            </tr>"""

        # Execution attempt details
        attempt_rows = ""
        for tc in data["test_cases"]:
            for ex in tc.get("execution_results", []):
                status_class = "pass" if ex["status"] == "passed" else "fail"
                attempt_rows += f"""
                <tr class="{status_class}">
                    <td>{ex['test_case_id']}</td>
                    <td>#{ex['attempt']}</td>
                    <td><strong>{ex['status'].upper()}</strong></td>
                    <td>{ex.get('error_type', '-')}</td>
                    <td>{ex.get('error_message', '-')[:80]}</td>
                    <td>{ex['duration_seconds']}s</td>
                    <td><a href="file:///{ex.get('log_file', '')}">Log</a></td>
                </tr>"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ShopEasy Test Automation Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #1a73e8; }}
        h2 {{ color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #1a73e8; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #eee; }}
        tr.pass td {{ background: #e8f5e9; }}
        tr.fail td {{ background: #fce4ec; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 150px; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #666; font-size: 14px; }}
        .summary-card .value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .passed .value {{ color: #2e7d32; }}
        .failed .value {{ color: #c62828; }}
        .total .value {{ color: #1a73e8; }}
        a {{ color: #1a73e8; }}
    </style>
</head>
<body>
    <h1>ShopEasy AI-Powered Test Automation Report</h1>
    <p>Generated: {data['report_generated']}</p>

    <div class="summary">
        <div class="summary-card total"><h3>Total</h3><div class="value">{summary['total_test_cases']}</div></div>
        <div class="summary-card passed"><h3>Passed</h3><div class="value">{summary['passed']}</div></div>
        <div class="summary-card failed"><h3>Failed</h3><div class="value">{summary['failed']}</div></div>
        <div class="summary-card"><h3>Attempts</h3><div class="value">{summary['total_attempts']}</div></div>
        <div class="summary-card"><h3>Duration</h3><div class="value">{summary['total_duration_s']}s</div></div>
    </div>

    <h2>Test Case Results</h2>
    <table>
        <tr><th>Test Case</th><th>Name</th><th>Status</th><th>Attempts</th><th>Steps</th><th>Duration</th></tr>
        {tc_rows}
    </table>

    <h2>Execution Attempts</h2>
    <table>
        <tr><th>Test Case</th><th>Attempt</th><th>Status</th><th>Error Type</th><th>Error Message</th><th>Duration</th><th>Log</th></tr>
        {attempt_rows}
    </table>
</body>
</html>"""

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

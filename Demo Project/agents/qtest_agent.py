"""
Mock Test Case Agent - Reads test case data from local JSON file.
For demo purposes - replaces the real qTest integration.
"""

import os
import json
import re
from agents.base_agent import BaseAgent


class QTestAgent(BaseAgent):
    """
    Agent that reads test cases from a local JSON file.
    Simulates the qTest API integration for demo purposes.
    """

    def __init__(self):
        super().__init__("QTestAgent")
        self._testcases = self._load_testcases()
        self.log_event("init", f"QTestAgent initialized with {len(self._testcases)} test cases from local data.")

    def _load_testcases(self):
        """Load test cases from the demo JSON file."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "demo_testcases.json")
        if not os.path.isfile(json_path):
            return []
        with open(json_path, encoding="utf-8") as f:
            loaded = json.load(f)
        return self._ensure_minimum_testcases(loaded, minimum=50)

    def _ensure_minimum_testcases(self, testcases, minimum=50):
        """Expand demo data deterministically so scalability screens have enough TCs."""
        if len(testcases) >= minimum or not testcases:
            return testcases

        expanded = list(testcases)
        source_count = len(testcases)
        while len(expanded) < minimum:
            idx = len(expanded)
            source = testcases[idx % source_count]
            clone = json.loads(json.dumps(source))
            clone["id"] = 90001 + idx
            clone["pid"] = f"TC-{idx + 1:03d}"
            clone["name"] = f"{source.get('name', 'Demo Test Case')} - Scale Variant {idx + 1:02d}"
            clone["description"] = (
                f"Scalable demo variant generated from {source.get('pid')}. "
                f"{source.get('description', '')}"
            )
            props = clone.setdefault("properties", {})
            props["Scale Variant"] = "true"
            props["Source Test Case"] = source.get("pid", "")
            expanded.append(clone)
        return expanded

    def fetch_test_case(self, test_case_id):
        """
        Fetch a single test case by PID (e.g., TC-001) or numeric ID.
        """
        self.start_timer()
        self.log_event("fetch_start", f"Fetching test case {test_case_id}")

        tc = None
        for item in self._testcases:
            if str(item.get("pid", "")) == str(test_case_id) or str(item.get("id", "")) == str(test_case_id):
                tc = item
                break

        if tc is None:
            raise ValueError(f"Test case '{test_case_id}' not found in demo data")

        # Parse steps
        steps = []
        for i, step in enumerate(tc.get("steps", [])):
            steps.append({
                "step_number": step.get("order", i + 1),
                "description": self._strip_html(step.get("description", "")),
                "expected_result": self._strip_html(step.get("expected", "")),
                "step_id": step.get("id", i + 1),
                "call_test_case_id": step.get("call_test_case_id"),
            })

        result = {
            "id": tc.get("id"),
            "pid": tc.get("pid", str(test_case_id)),
            "name": tc.get("name", ""),
            "description": tc.get("description", ""),
            "precondition": tc.get("precondition", ""),
            "properties": tc.get("properties", {}),
            "steps": steps,
            "step_count": len(steps),
            "raw": tc,
        }

        self.log_event("fetch_complete",
                        f"Fetched {result['pid']}: '{result['name'][:60]}' with {len(steps)} steps",
                        {"pid": result["pid"], "step_count": len(steps),
                         "elapsed_s": self.elapsed_seconds()})
        return result

    def fetch_non_automated_test_cases(self, limit=10):
        """Return test cases that don't have automation status set."""
        self.start_timer()
        self.log_event("search_start", "Searching for non-automated test cases")

        results = []
        for tc in self._testcases:
            props = tc.get("properties", {})
            auto_status = props.get("Automation Status", "")
            if not auto_status:
                steps = []
                for i, step in enumerate(tc.get("steps", [])):
                    steps.append({
                        "step_number": step.get("order", i + 1),
                        "description": self._strip_html(step.get("description", "")),
                        "expected_result": self._strip_html(step.get("expected", "")),
                        "step_id": step.get("id", i + 1),
                        "call_test_case_id": step.get("call_test_case_id"),
                    })
                results.append({
                    "id": tc.get("id"),
                    "pid": tc.get("pid"),
                    "name": tc.get("name", ""),
                    "description": tc.get("description", ""),
                    "precondition": tc.get("precondition", ""),
                    "properties": props,
                    "steps": steps,
                    "step_count": len(steps),
                })
                if limit and len(results) >= limit:
                    break

        self.log_event("search_complete",
                        f"Found {len(results)} non-automated test cases",
                        {"count": len(results), "elapsed_s": self.elapsed_seconds()})
        return results

    @staticmethod
    def _strip_html(text):
        """Remove HTML tags from text."""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', ' ', str(text))
        clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&')
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&#39;', "'").replace('&quot;', '"')
        return re.sub(r'\s+', ' ', clean).strip()

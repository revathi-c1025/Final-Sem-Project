from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


class FeedbackDrivenImprovement:
    """Learns lightweight mapping hints from execution evidence."""

    def analyze(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        failures = [
            failure
            for tc in test_cases
            for failure in tc.get("failures", [])
        ]
        categories = Counter(failure.get("category", "unknown") for failure in failures)
        hints = []
        if categories.get("product_issue"):
            hints.append("Strengthen expected-result extraction and response-field assertions.")
        if categories.get("script_issue"):
            hints.append("Prefer existing framework helpers over newly generated helper calls.")
        if categories.get("environment_issue"):
            hints.append("Surface environment prerequisites before execution starts.")
        if not hints:
            hints.append("Current mappings are stable for the executed scenario.")
        return {"failure_categories": dict(categories), "mapping_hints": hints}


class ExtendedDomainSupport:
    """Detects protocol coverage needed by test steps."""

    def inspect(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        text = " ".join(
            f"{tc.get('test_case_name', '')} {tc.get('test_case_id', '')}"
            for tc in test_cases
        ).lower()
        supported = ["REST"]
        detected = []
        for label, pattern in {
            "GraphQL": r"graphql|mutation|query\s*\{",
            "gRPC": r"\bgrpc\b|protobuf|proto service",
            "Event-driven": r"webhook|kafka|event|queue|topic",
        }.items():
            if re.search(pattern, text):
                detected.append(label)
        return {
            "active_protocol": "REST",
            "supported_extensions": supported + ["GraphQL adapter", "gRPC adapter", "Event adapter"],
            "detected_non_rest_needs": detected,
        }


class SelfHealingTestRepair:
    """Creates deterministic repair advice for failed executions."""

    def recommend(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        recommendations = []
        for tc in test_cases:
            for failure in tc.get("failures", []):
                category = failure.get("category", "unknown")
                if category == "script_issue":
                    recommendations.append({
                        "test_case_id": tc.get("test_case_id"),
                        "action": "Regenerate test using existing helper-method inventory.",
                    })
                elif category == "product_issue":
                    recommendations.append({
                        "test_case_id": tc.get("test_case_id"),
                        "action": "Keep script unchanged and request product-owner review.",
                    })
                elif category == "environment_issue":
                    recommendations.append({
                        "test_case_id": tc.get("test_case_id"),
                        "action": "Block autonomous retry until environment inputs are corrected.",
                    })
        if not recommendations:
            recommendations.append({"action": "No repair needed for this run."})
        return {"recommendations": recommendations, "requires_human_review": True}


class CrossRepoIntelligence:
    """Summarizes reusable automation patterns from local reference repositories."""

    def scan(self, root: str | Path = "demo_reference_tests") -> dict[str, Any]:
        root_path = Path(root)
        if not root_path.exists():
            return {"reference_tests": 0, "helper_modules": 0, "patterns": []}

        test_files = list(root_path.rglob("test_*.py"))
        helper_files = list(root_path.rglob("*_task.py")) + list(root_path.rglob("*_flow.py"))
        patterns = sorted({
            "task-object pattern" if "_task.py" in str(path) else "workflow helper pattern"
            for path in helper_files
        })
        return {
            "reference_tests": len(test_files),
            "helper_modules": len(helper_files),
            "patterns": patterns,
        }


class ProactiveGapDetection:
    """Predicts coverage gaps from executed TC metadata."""

    def detect(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        names = " ".join(tc.get("test_case_name", "") for tc in test_cases).lower()
        expected_domains = {
            "products": "product",
            "categories": "categor",
            "cart": "cart",
            "orders": "order",
            "users": "user",
            "inventory": "inventory",
            "payments": "payment",
            "notifications": "notification",
        }
        covered = [domain for domain, token in expected_domains.items() if token in names]
        gaps = [domain for domain in expected_domains if domain not in covered]
        return {
            "covered_domains": covered,
            "predicted_gaps": gaps,
            "risk": "low" if len(gaps) <= 2 else "medium" if len(gaps) <= 5 else "high",
        }


def build_research_extension_report(test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "feedback_driven_improvement": FeedbackDrivenImprovement().analyze(test_cases),
        "extended_domain_support": ExtendedDomainSupport().inspect(test_cases),
        "self_healing_test_repair": SelfHealingTestRepair().recommend(test_cases),
        "cross_repo_intelligence": CrossRepoIntelligence().scan(),
        "proactive_gap_detection": ProactiveGapDetection().detect(test_cases),
        "guardrails": [
            "Performance, load, security, and scalability testing are supported as controlled demo modes, not production stress execution.",
            "Fully autonomous execution in shared or production environments requires an external human approval gate.",
            "Infrastructure provisioning and CI/CD orchestration are assumed to exist externally.",
        ],
    }


def persist_feedback_snapshot(report: dict[str, Any], path: str | Path = "output/feedback_improvements.json") -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

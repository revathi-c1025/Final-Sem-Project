from __future__ import annotations

from .models import IRStep


class RetrieverAgent:
    """Provides small deterministic context for code generation."""

    def retrieve(self, steps: list[IRStep]) -> dict[str, str]:
        methods = sorted({step.http_method for step in steps})
        endpoints = ", ".join(step.object for step in steps)
        return {
            "style": "Generate plain pytest functions using requests only.",
            "methods": ", ".join(methods),
            "endpoints": endpoints,
        }

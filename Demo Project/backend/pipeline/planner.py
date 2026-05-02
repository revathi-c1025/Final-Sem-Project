from __future__ import annotations

from .models import IRStep


class PlannerAgent:
    """Orders IR steps while preserving declared dependencies."""

    def plan(self, steps: list[IRStep]) -> list[IRStep]:
        planned: list[IRStep] = []
        remaining = list(enumerate(steps, start=1))

        while remaining:
            progressed = False
            completed = {f"step_{idx}" for idx, _ in enumerate(planned, start=1)}
            for original_index, step in list(remaining):
                if all(dep in completed or dep == f"step_{original_index - 1}" for dep in step.dependencies):
                    planned.append(step)
                    remaining.remove((original_index, step))
                    progressed = True
            if not progressed:
                planned.extend(step for _, step in remaining)
                break

        return planned

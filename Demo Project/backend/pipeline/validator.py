from __future__ import annotations

import ast

from .models import IRStep, ValidationResult


class ValidatorAgent:
    ALLOWED_IMPORTS = {"os", "pytest", "requests"}

    def validate(self, code: str, steps: list[IRStep]) -> ValidationResult:
        errors: list[str] = []

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return ValidationResult(valid=False, errors=[f"SyntaxError: {exc}"])

        imported = self._collect_imports(tree)
        disallowed = imported - self.ALLOWED_IMPORTS
        if disallowed:
            errors.append(f"Disallowed imports: {', '.join(sorted(disallowed))}")

        for required in ("pytest", "requests"):
            if required not in imported:
                errors.append(f"Missing required import: {required}")

        expected_cases = len(steps)
        actual_cases = code.count('"expected_status"') + code.count("'expected_status'")
        if actual_cases < expected_cases:
            errors.append(f"Only generated {actual_cases} cases for {expected_cases} IR steps")

        if "requests.request(" not in code:
            errors.append("Generated code does not call requests.request")

        if "assert response.status_code ==" not in code:
            errors.append("Generated code does not assert response status code")

        return ValidationResult(valid=not errors, errors=errors)

    def _collect_imports(self, tree: ast.AST) -> set[str]:
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        return imports

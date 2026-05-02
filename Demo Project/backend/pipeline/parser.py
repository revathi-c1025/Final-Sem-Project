from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

from .models import IRStep


class IRParser:
    """Converts natural-language API steps into a small intermediate representation."""

    METHOD_PATTERN = re.compile(r"\b(GET|POST|PUT|DELETE)\b", re.IGNORECASE)
    STATUS_PATTERN = re.compile(
        r"(?:status(?:\s+code)?|returns?|responds?\s+with|expect(?:ed)?|should\s+be)\D{0,20}"
        r"\b([1-5][0-9]{2})\b",
        re.IGNORECASE,
    )
    ENDPOINT_PATTERN = re.compile(
        r"(https?://[^\s,;]+|/[A-Za-z0-9_./{}:?\-&=%]+)"
    )
    QUOTED_ENDPOINT_PATTERN = re.compile(r"endpoint\s+['\"]([^'\"]+)['\"]", re.IGNORECASE)

    def parse(self, steps: list[str]) -> list[IRStep]:
        return [self.parse_step(step, index) for index, step in enumerate(steps, start=1)]

    def parse_step(self, step: str, index: int) -> IRStep:
        method = self._extract_method(step)
        endpoint = self._extract_endpoint(step)
        status_code = self._extract_status_code(step)
        inputs = self._extract_inputs(step, endpoint)
        dependencies = self._extract_dependencies(step, index)

        return IRStep(
            action=self._action_for(method),
            object=endpoint,
            inputs=inputs,
            expected_result=f"status_code == {status_code}",
            http_method=method,
            auth_type=self._extract_auth_type(step),
            dependencies=dependencies,
        )

    def _extract_method(self, step: str) -> str:
        match = self.METHOD_PATTERN.search(step)
        if match:
            return match.group(1).upper()

        lowered = step.lower()
        if any(word in lowered for word in ["create", "register", "login", "submit"]):
            return "POST"
        if any(word in lowered for word in ["update", "replace", "modify"]):
            return "PUT"
        if any(word in lowered for word in ["delete", "remove"]):
            return "DELETE"
        return "GET"

    def _extract_endpoint(self, step: str) -> str:
        quoted = self.QUOTED_ENDPOINT_PATTERN.search(step)
        if quoted:
            return quoted.group(1).strip()

        match = self.ENDPOINT_PATTERN.search(step)
        if match:
            return match.group(1).rstrip(".")

        return "/"

    def _extract_status_code(self, step: str) -> int:
        match = self.STATUS_PATTERN.search(step)
        if match:
            return int(match.group(1))

        method = self._extract_method(step)
        if method == "POST":
            return 201
        if method == "DELETE":
            return 204
        return 200

    def _extract_auth_type(self, step: str) -> str:
        lowered = step.lower()
        if "basic auth" in lowered:
            return "Basic"
        if "no auth" in lowered or "without auth" in lowered:
            return "None"
        return "Bearer"

    def _extract_dependencies(self, step: str, index: int) -> list[str]:
        lowered = step.lower()
        if index > 1 and any(token in lowered for token in ["then", "after", "using", "from previous"]):
            return [f"step_{index - 1}"]
        return []

    def _extract_inputs(self, step: str, endpoint: str) -> dict[str, Any]:
        inputs: dict[str, Any] = {"endpoint": endpoint}
        body = self._extract_json_body(step)
        if body is not None:
            inputs["json"] = body

        token_env = self._extract_token_env(step)
        if token_env:
            inputs["token_env"] = token_env

        parsed = urlparse(endpoint)
        if parsed.query:
            inputs["query"] = parsed.query

        return inputs

    def _extract_json_body(self, step: str) -> Any | None:
        match = re.search(r"(\{.*\}|\[.*\])", step)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

    def _extract_token_env(self, step: str) -> str | None:
        match = re.search(r"(?:token|bearer)\s+(?:from\s+)?(?:env\s+)?([A-Z][A-Z0-9_]+)", step)
        if match:
            return match.group(1)
        return None

    def _action_for(self, method: str) -> str:
        return {
            "GET": "retrieve",
            "POST": "create",
            "PUT": "update",
            "DELETE": "delete",
        }.get(method, "call")

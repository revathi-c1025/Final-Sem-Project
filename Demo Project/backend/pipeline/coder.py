from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import IRStep


class CoderAgent:
    """Generates executable pytest code from planned IR steps."""

    def generate(self, steps: list[IRStep], context: dict[str, str] | None = None, feedback: str = "") -> str:
        lines: list[str] = [
            "import os",
            "",
            "import pytest",
            "import requests",
            "",
            "",
            "BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8001')",
            "DEFAULT_TOKEN = os.environ.get('API_TOKEN', '')",
            "",
            "",
            "def build_url(endpoint):",
            "    if endpoint.startswith('http://') or endpoint.startswith('https://'):",
            "        return endpoint",
            "    return BASE_URL.rstrip('/') + '/' + endpoint.lstrip('/')",
            "",
            "",
            "def auth_headers(auth_type='Bearer', token_env=None):",
            "    if auth_type == 'None':",
            "        return {}",
            "    token = os.environ.get(token_env, '') if token_env else DEFAULT_TOKEN",
            "    if not token:",
            "        return {}",
            "    if auth_type == 'Basic':",
            "        return {'Authorization': 'Basic ' + token}",
            "    return {'Authorization': 'Bearer ' + token}",
            "",
            "",
            "@pytest.mark.parametrize('case', [",
        ]

        for index, step in enumerate(steps, start=1):
            case = {
                "name": f"step_{index}_{self._slug(step.http_method + '_' + step.object)}",
                "method": step.http_method,
                "endpoint": step.object,
                "expected_status": self._expected_status(step.expected_result),
                "auth_type": step.auth_type,
                "token_env": step.inputs.get("token_env"),
                "json": step.inputs.get("json"),
            }
            lines.append(f"    {repr(case)},")

        lines.extend(
            [
                "])",
                "def test_generated_api_step(case):",
                "    response = requests.request(",
                "        case['method'],",
                "        build_url(case['endpoint']),",
                "        headers=auth_headers(case['auth_type'], case.get('token_env')),",
                "        json=case.get('json'),",
                "        timeout=15,",
                "    )",
                "    assert response.status_code == case['expected_status']",
                "",
            ]
        )

        return "\n".join(lines)

    def _expected_status(self, expected_result: str) -> int:
        match = re.search(r"\b([1-5][0-9]{2})\b", expected_result)
        if match:
            return int(match.group(1))
        return 200

    def _slug(self, value: str) -> str:
        parsed = urlparse(value)
        source = parsed.path if parsed.scheme else value
        slug = re.sub(r"[^A-Za-z0-9]+", "_", source).strip("_").lower()
        return slug or "root"

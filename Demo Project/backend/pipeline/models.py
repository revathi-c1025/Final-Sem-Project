from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]


class GenerateTestRequest(BaseModel):
    steps: list[str] = Field(..., min_length=1)


class IRStep(BaseModel):
    action: str = ""
    object: str = ""
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected_result: str = ""
    http_method: HttpMethod = "GET"
    auth_type: str = "Bearer"
    dependencies: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    status: Literal["success", "failure"]
    logs: str = ""
    errors: str = ""
    return_code: int = 0
    test_file: str = ""


class GenerateTestResponse(BaseModel):
    generated_code: str
    status: Literal["success", "failure"]
    logs: str = ""
    errors: str = ""

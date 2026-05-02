from __future__ import annotations

from .coder import CoderAgent
from .executor import ExecutionEngine
from .models import GenerateTestResponse
from .parser import IRParser
from .planner import PlannerAgent
from .retriever import RetrieverAgent
from .validator import ValidatorAgent


class TestGenerationService:
    def __init__(self) -> None:
        self.parser = IRParser()
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent()
        self.coder = CoderAgent()
        self.validator = ValidatorAgent()
        self.executor = ExecutionEngine()

    def generate_and_execute(self, raw_steps: list[str]) -> GenerateTestResponse:
        ir_steps = self.parser.parse(raw_steps)
        planned_steps = self.planner.plan(ir_steps)
        context = self.retriever.retrieve(planned_steps)

        feedback = ""
        generated_code = ""
        validation_errors: list[str] = []

        for _attempt in range(1, 4):
            generated_code = self.coder.generate(planned_steps, context=context, feedback=feedback)
            validation = self.validator.validate(generated_code, planned_steps)
            if validation.valid:
                execution = self.executor.execute(generated_code)
                return GenerateTestResponse(
                    generated_code=generated_code,
                    status=execution.status,
                    logs=execution.logs,
                    errors=execution.errors,
                )

            validation_errors = validation.errors
            feedback = "\n".join(validation_errors)

        return GenerateTestResponse(
            generated_code=generated_code,
            status="failure",
            logs="Validation failed after 3 attempts.",
            errors="\n".join(validation_errors),
        )

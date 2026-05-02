from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .pipeline.models import GenerateTestRequest, GenerateTestResponse
from .pipeline.service import TestGenerationService


app = FastAPI(title="AI Test Automation Framework", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = TestGenerationService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate-test", response_model=GenerateTestResponse)
def generate_test(payload: GenerateTestRequest) -> GenerateTestResponse:
    return service.generate_and_execute(payload.steps)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

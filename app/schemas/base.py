from pydantic import BaseModel
from typing import Optional


class GenerationRequest(BaseModel):
    prompt: str
    preprocessor: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: str
    error_code: str

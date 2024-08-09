import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LLMResultSchema(BaseModel):
    id: uuid.UUID
    model: str
    prompt: str
    response: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

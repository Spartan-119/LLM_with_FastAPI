import hashlib
import uuid

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class LLMResult(Base):
    """
    Model representing the result of a language model generation task.
    """

    __tablename__ = "llm_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model = Column(String, index=True)  # Name of the LLM model used
    prompt = Column(Text)  # Input prompt for the generation task
    prompt_hash = Column(String(64), index=True)  # SHA256 hash for caching
    response = Column(Text, nullable=True)  # Generated response from the LLM
    status = Column(
        String, default="pending", index=True
    )  # Status of the generation task
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Timestamp of task creation
    completed_at = Column(
        DateTime(timezone=True), nullable=True
    )  # Timestamp of task completion

    @staticmethod
    def generate_prompt_hash(model: str, prompt: str) -> str:
        """
        Generate a unique hash for a given model and prompt combination.
        This is used for caching purposes.
        """
        return hashlib.sha256(f"{model}:{prompt}".encode()).hexdigest()


class User(Base):
    """
    Model representing a user in the system.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Stores the hashed password, not the plain text
    is_active = Column(Boolean, default=True)  # Indicates if the user account is active

    # Potential additional fields:
    # email = Column(String, unique=True, index=True)
    # full_name = Column(String)
    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # last_login = Column(DateTime(timezone=True), nullable=True)

    # Potential relationship:
    # results = relationship("LLMResult", back_populates="user")

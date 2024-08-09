import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.schemas.user import UserCreate

# Set up password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generate a hash for a given password."""
    return pwd_context.hash(password)


async def create_llm_result(
    db: AsyncSession, model: str, prompt: str
) -> models.LLMResult:
    """Create a new LLMResult entry in the database."""
    prompt_hash = models.LLMResult.generate_prompt_hash(model, prompt)
    db_result = models.LLMResult(model=model, prompt=prompt, prompt_hash=prompt_hash)
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)
    return db_result


async def get_llm_result(db: AsyncSession, result_id: uuid.UUID) -> models.LLMResult:
    """Retrieve an LLMResult by its ID."""
    result = await db.execute(
        select(models.LLMResult).filter(models.LLMResult.id == result_id)
    )
    return result.scalar_one_or_none()


async def update_llm_result(
    db: AsyncSession, result_id: uuid.UUID, response: str, status: str
) -> models.LLMResult:
    """Update an existing LLMResult with a response and status."""
    db_result = await get_llm_result(db, result_id)
    if db_result:
        db_result.response = response
        db_result.status = status
        db_result.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_result)
    return db_result


async def get_cached_result(
    db: AsyncSession, model: str, prompt: str
) -> models.LLMResult:
    """Retrieve a cached LLMResult for a given model and prompt."""
    prompt_hash = models.LLMResult.generate_prompt_hash(model, prompt)
    result = await db.execute(
        select(models.LLMResult).filter(
            models.LLMResult.prompt_hash == prompt_hash,
            models.LLMResult.status == "completed",
        )
    )
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, username: str) -> models.User:
    """Retrieve a user by username."""
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> models.User:
    """Create a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> models.User | None:
    """Authenticate a user by username and password."""
    user = await get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

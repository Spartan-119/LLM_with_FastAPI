import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi import FastAPI, APIRouter, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    LLMHubException,
    ModelNotFoundException,
    OllamaServiceException,
)
from app.core.logger import log_error, log_info
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_token,
)
from app.core.tasks import generate_text
from app.db import crud
from app.db.base import get_db
from app.schemas.base import GenerationRequest, ErrorResponse
from app.schemas.llm import LLMResultSchema
from app.schemas.token import Token
from app.schemas.user import User
from app.services.ollama import ollama_service
from app.utils.preprocessors import PREPROCESSORS

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

# Create API router for version 1
v1_router = APIRouter(prefix="/v1")


@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and provide access token.
    """
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh_token", response_model=Token, tags=["authentication"])
async def refresh_access_token(refresh_token: str):
    """
    Use refresh token to get a new access token.
    """
    try:
        token_data = verify_token(refresh_token)
        access_token = create_access_token(data={"sub": token_data.username})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


# Exception handlers
@app.exception_handler(LLMHubException)
async def llm_hub_exception_handler(request, exc: LLMHubException):
    log_error(exc, error_code=exc.error_code)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error", detail=exc.message, error_code=exc.error_code
        ).dict(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    log_error(exc, error_code="VALIDATION_ERROR")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error", detail=str(exc), error_code="VALIDATION_ERROR"
        ).dict(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    log_error(exc, status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Exception",
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
        ).dict(),
    )


# Middleware for logging requests and responses
@app.middleware("http")
async def log_requests(request, call_next):
    log_info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    log_info(f"Response: {response.status_code}")
    return response


@app.get("/", tags=["root"])
async def read_root():
    """
    Root endpoint to verify API is running.
    """
    log_info("Root endpoint accessed")
    return {"message": "Welcome to LLM Hub"}


@v1_router.get("/models", tags=["models"])
async def list_models():
    """
    Retrieve a list of available language models.
    """
    try:
        available_models = await ollama_service.get_available_models()
        log_info("Available models retrieved", models=available_models)
        return {"models": available_models}
    except OllamaServiceException as e:
        raise LLMHubException(str(e), "OLLAMA_SERVICE_ERROR")


@v1_router.post(
    "/generate/{model}",
    response_model=LLMResultSchema,
    tags=["generation"],
    summary="Generate text using a specified model",
    description="Generate text using the specified model, with optional preprocessing and caching.",
)
async def generate(
    model: str,
    request: GenerationRequest,
    preprocessor: Optional[str] = Query(
        None, description="Name of the preprocessor function to apply"
    ),
    use_cache: bool = Query(default=True, description="Whether to use cached results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Ensure model has a version tag
        if ":" not in model:
            model += ":latest"

        prompt = request.prompt
        if preprocessor:
            if preprocessor not in PREPROCESSORS:
                raise HTTPException(
                    status_code=400, detail=f"Preprocessor '{preprocessor}' not found"
                )
            prompt = PREPROCESSORS[preprocessor](prompt)

        # Check cache for existing results
        if use_cache:
            cached_result = await crud.get_cached_result(db, model, prompt)
            if cached_result:
                log_info("Cached result found", model=model, prompt=prompt)
                return LLMResultSchema.from_orm(cached_result)

        # Verify model availability
        available_models = await ollama_service.get_available_models()
        if model not in available_models:
            raise ModelNotFoundException(model)

        # Create new result entry and start generation task
        db_result = await crud.create_llm_result(db, model, prompt)
        generate_text.apply_async(args=[str(db_result.id), model, prompt])
        log_info("Generation task created", model=model, task_id=str(db_result.id))
        return LLMResultSchema.from_orm(db_result)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, operation="generate", model=model, prompt=prompt)
        raise LLMHubException("Failed to generate text", "GENERATION_ERROR")


@v1_router.get(
    "/result/{result_id}",
    response_model=LLMResultSchema,
    tags=["results"],
    summary="Retrieve generation result",
    description="Fetch the result of a text generation task by its ID.",
)
async def get_result(result_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    db_result = await crud.get_llm_result(db, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="Result not found")
    log_info("Result retrieved", result_id=str(result_id))
    return LLMResultSchema.from_orm(db_result)


# Include v1 router in the main app
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

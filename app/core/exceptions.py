from fastapi import HTTPException


class LLMHubException(Exception):
    """
    Base exception class for LLM Hub.
    All custom exceptions in the application should inherit from this.
    """

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ModelNotFoundException(LLMHubException):
    """
    Exception raised when a requested model is not found.
    """

    def __init__(self, model: str):
        super().__init__(f"Model {model} not found", "MODEL_NOT_FOUND")


class OllamaServiceException(LLMHubException):
    """
    Exception raised when there's an error with the Ollama service.
    """

    def __init__(self, message: str):
        super().__init__(message, "OLLAMA_SERVICE_ERROR")


class DatabaseException(LLMHubException):
    """
    Exception raised when there's a database-related error.
    """

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class CeleryTaskException(LLMHubException):
    """
    Exception raised when there's an error with a Celery task.
    """

    def __init__(self, message: str):
        super().__init__(message, "CELERY_TASK_ERROR")


def llm_hub_exception_handler(exc: LLMHubException):
    """
    Global exception handler for LLMHubException.
    Converts LLMHubException to FastAPI's HTTPException for proper API responses.
    """
    return HTTPException(
        status_code=500, detail={"message": exc.message, "error_code": exc.error_code}
    )

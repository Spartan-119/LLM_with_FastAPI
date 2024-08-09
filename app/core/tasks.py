import asyncio
import uuid

from sqlalchemy.exc import SQLAlchemyError

from app.core.celery_app import celery_app
from app.core.logger import logger
from app.db import crud
from app.db.base import AsyncSessionLocal
from app.services.ollama import ollama_service, OllamaServiceException


@celery_app.task(bind=True, max_retries=3)
def generate_text(self, result_id: str, model: str, prompt: str):
    """
    Celery task for generating text using the Ollama service.

    This task is set to retry up to 3 times in case of failures.

    Args:
        result_id (str): The UUID of the LLMResult to update.
        model (str): The name of the model to use for text generation.
        prompt (str): The input prompt for text generation.

    Returns:
        str: The generated text response.
    """

    async def _generate():
        async with AsyncSessionLocal() as db:
            try:
                # Attempt to generate text using the Ollama service
                result = await ollama_service.generate_text(model, prompt)

                # Update the database with the generated result
                await crud.update_llm_result(
                    db, uuid.UUID(result_id), result["response"], "completed"
                )

                # Log successful completion
                logger.info(
                    f"Text generation completed for model {model}",
                    extra={
                        "result_id": result_id,
                        "model": model,
                        "prompt_length": len(prompt),
                    },
                )
                return result["response"]

            except OllamaServiceException as e:
                # Handle Ollama service-specific errors
                logger.error(
                    f"Ollama service error in generate_text task: {str(e)}",
                    extra={"result_id": result_id, "model": model, "error": str(e)},
                )
                await crud.update_llm_result(
                    db, uuid.UUID(result_id), f"Error: {str(e)}", "failed"
                )
                # Retry the task with exponential backoff
                raise self.retry(exc=e, countdown=2**self.request.retries)

            except SQLAlchemyError as e:
                # Handle database-related errors
                logger.error(
                    f"Database error in generate_text task: {str(e)}",
                    extra={"result_id": result_id, "model": model, "error": str(e)},
                )
                raise

            except Exception as e:
                # Handle any other unexpected errors
                logger.error(
                    f"Unexpected error in generate_text task: {str(e)}",
                    extra={"result_id": result_id, "model": model, "error": str(e)},
                )
                await crud.update_llm_result(
                    db, uuid.UUID(result_id), f"Error: {str(e)}", "failed"
                )
                raise

    # Run the asynchronous function in the synchronous Celery task
    return asyncio.get_event_loop().run_until_complete(_generate())

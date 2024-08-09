from typing import List, Dict, Any

import httpx

from app.core.config import settings
from app.core.exceptions import OllamaServiceException
from app.core.logger import log_error, log_info


class OllamaService:
    def __init__(self, base_url: str = settings.OLLAMA_URL):
        self.base_url = base_url

    async def get_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=60)
                response.raise_for_status()
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                log_info("Retrieved available models", count=len(model_names))
                return model_names
        except httpx.HTTPStatusError as e:
            log_error(
                e, operation="get_available_models", status_code=e.response.status_code
            )
            raise OllamaServiceException(
                f"Ollama service returned status code {e.response.status_code}"
            )
        except Exception as e:
            log_error(e, operation="get_available_models")
            raise OllamaServiceException("Failed to fetch models from Ollama")

    async def generate_text(self, model: str, prompt: str) -> Dict[str, Any]:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=600,
                )
                response.raise_for_status()
                result = response.json()
                log_info(
                    "Text generated successfully",
                    model=model,
                    prompt_length=len(prompt),
                )
                return result
        except httpx.HTTPStatusError as e:
            log_error(
                e,
                operation="generate_text",
                model=model,
                status_code=e.response.status_code,
            )
            raise OllamaServiceException(
                f"Ollama service returned status code {e.response.status_code}"
            )
        except httpx.RequestError as e:
            log_error(e, operation="generate_text", model=model)
            raise OllamaServiceException("Failed to connect to Ollama service")
        except Exception as e:
            log_error(e, operation="generate_text", model=model)
            raise OllamaServiceException("Failed to generate text with Ollama")

    async def chat(self, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json={"model": model, "messages": messages},
                    timeout=600,
                )
                response.raise_for_status()
                result = response.json()
                log_info(
                    "Chat completed successfully",
                    model=model,
                    message_count=len(messages),
                )
                return result
        except httpx.HTTPStatusError as e:
            log_error(
                e, operation="chat", model=model, status_code=e.response.status_code
            )
            raise OllamaServiceException(
                f"Ollama service returned status code {e.response.status_code}"
            )
        except httpx.RequestError as e:
            log_error(e, operation="chat", model=model)
            raise OllamaServiceException("Failed to connect to Ollama service")
        except Exception as e:
            log_error(e, operation="chat", model=model)
            raise OllamaServiceException("Failed to chat with Ollama")


ollama_service = OllamaService()

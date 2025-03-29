from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config
import httpx
import logging


# .......................................................................................


class BaseAgent:
    """Base agent class with common functionality."""

    def __init__(
        self, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.1
    ):
        """Initialize the base agent with model configuration."""
        self.config = Config
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._load_model()
        self.output_parser = StrOutputParser()

    def _load_model(self) -> BaseLanguageModel:
        """Load the language model based on configuration."""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.config.get("GEMINI_API_KEY"),
        )

    def create_chain(self, prompt_template: str):
        """Create a processing chain with the prompt template."""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | self.llm | self.output_parser

    def format_response(self, response: str, thread_id: str) -> Dict[str, Any]:
        """Format the model's response with metadata."""
        return {
            "content": response,
            "thread_id": thread_id,
            "metadata": {"model": self.model_name, "temperature": self.temperature},
        }

    async def make_http_request(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to external API endpoints.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: The URL to call
            json: Optional JSON payload for POST/PUT requests
            params: Optional query parameters
            headers: Optional HTTP headers

        Returns:
            Dictionary containing response data or error information
        """
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, json=json, params=params, headers=headers
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, json=json, params=params, headers=headers
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported HTTP method: {method}",
                    }

                if response.status_code >= 200 and response.status_code < 300:
                    return {
                        "success": True,
                        "data": response.json(),
                        "status_code": response.status_code,
                    }
                else:
                    error_msg = (
                        f"HTTP request failed with status code {response.status_code}"
                    )
                    logging.error(f"{error_msg}: {response.text}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                    }

        except Exception as e:
            error_msg = f"Error making HTTP request to {url}: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

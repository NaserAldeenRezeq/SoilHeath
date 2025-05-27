"""
google_llm.py

This module defines the `GoogleLLM` class, which provides an interface
for interacting with the Google Generative AI API. It extends a base LLM interface 
to support initialization, configuration, and text generation.

Classes:
    GoogleLLM: A wrapper class that initializes and interacts with the 
    Google Generative AI API to generate text.

Raises:
    RuntimeError or ValueError with descriptive error messages for 
    configuration or generation failures.
"""

import os
import sys
import logging
from typing import Optional

try:
    import google.generativeai as genai

    CURRENT_DIR = os.path.dirname(__file__)
    MAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../"))

    if not os.path.exists(MAIN_DIR):
        MAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
        if not os.path.exists(MAIN_DIR):
            raise FileNotFoundError(
                f"Project directory not found. Attempted: {os.path.join(CURRENT_DIR, '../')} "
                f"and {os.path.join(CURRENT_DIR, '../../')}"
            )

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.helpers import get_settings, Settings
    from src.enums import GoogleLLMLog
    from .abc_llm import ILLMsGenerators

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
    raise
except FileNotFoundError as e:
    logging.error("Project directory not found: %s", e, exc_info=True)
    raise
except (RuntimeError, ValueError) as e:
    logging.critical("Unexpected setup error in google_llm.py: %s", e, exc_info=True)
    raise


class GoogleLLM(ILLMsGenerators):
    """
    A class that integrates a Google Generative AI model with a customizable interface.

    Attributes:
        app_settings (Settings): Application-wide configuration including API keys.
        model (genai.GenerativeModel): Google AI GenerativeModel instance.
        model_name (str): Name of the model used for generation.
        generation_config (genai.types.GenerationConfig): Configuration for generation parameters.
    """

    def __init__(self):
        """Initializes the GoogleLLM instance by loading application settings."""
        try:
            self.app_settings: Settings = get_settings()
            self.model: Optional[genai.GenerativeModel] = None
            self.model_name: str = ""
            self.generation_config: Optional[genai.types.GenerationConfig] = None
        except Exception as e:
            log_error(GoogleLLMLog.INIT_SETTINGS_FAIL.value + f": {e}")
            raise RuntimeError(GoogleLLMLog.INIT_FAILED.value) from e

    # pylint: disable= too-many-arguments
    # pylint: disable= arguments-differ
    # pylint: disable= too-many-positional-arguments
    def initialize_llm(
        self,
        model_name: str = "gemini-1.0-pro",
        max_new_tokens: int = 1024,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None
    ):
        """
        Configures the Google AI client and sets generation parameters.

        Args:
            model_name (str): The model identifier. Default is "gemini-1.0-pro".
            max_new_tokens (int): Max tokens to generate. Default is 1024.
            temperature (float, optional): Sampling temperature. Default is 0.7.
            top_p (float, optional): Nucleus sampling parameter.
            top_k (int, optional): Top-k sampling parameter.

        Raises:
            ValueError: If the API key is missing or invalid.
            RuntimeError: If initialization fails for other reasons.
        """
        try:
            api_key = self.app_settings.GOOGLE_API_KEY
            if not api_key:
                raise ValueError(GoogleLLMLog.MISSING_API_KEY.value)

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name

            config_params = {
                "max_output_tokens": max_new_tokens
            }
            if temperature is not None:
                config_params["temperature"] = temperature
            if top_p is not None:
                config_params["top_p"] = top_p
            if top_k is not None:
                config_params["top_k"] = top_k

            self.generation_config = genai.types.GenerationConfig(**config_params)

            log_info(GoogleLLMLog.INITIALIZED_SUCCESSFULLY.value)
            log_info(
                f"Config: model={model_name}, temp={temperature}, "
                f"top_p={top_p}, top_k={top_k}, tokens={max_new_tokens}"
            )
        except ValueError as ve:
            log_error(GoogleLLMLog.VALUE_ERROR_INIT.value + f": {ve}")
            raise
        except Exception as e:
            log_error(GoogleLLMLog.INIT_FAILED.value + f": {e}")
            raise RuntimeError(GoogleLLMLog.INIT_FAILED.value) from e

    def generate_response(self, prompt: str) -> str:
        """
        Generates a text response using the configured Google AI model.

        Args:
            prompt (str): The input prompt string.

        Returns:
            str: Generated text response.

        Raises:
            RuntimeError: If generation fails or model is not initialized.
        """
        try:
            if not self.model or not self.generation_config:
                raise RuntimeError(GoogleLLMLog.MODEL_NOT_INITIALIZED.value)

            log_info(GoogleLLMLog.GENERATION_STARTED.value)
            response = self.model.generate_content(
                prompt, generation_config=self.generation_config
            )

            if response and hasattr(response, 'text'):
                log_info(GoogleLLMLog.GENERATED_RESPONSE.value)
                return response.text.strip()
            elif response and hasattr(response, 'parts'):
                result = "".join(part.text 
                                 for part in response.parts 
                                 if hasattr(part, 'text')).strip()
                log_info(GoogleLLMLog.GENERATED_RESPONSE.value)
                return result
            else:
                log_error(GoogleLLMLog.INVALID_RESPONSE.value + f" | Response: {response}")
                raise RuntimeError(GoogleLLMLog.INVALID_RESPONSE.value)
        except Exception as e:
            log_error(GoogleLLMLog.TEXT_GEN_FAILED.value + f": {e}")
            if "API key not valid" in str(e):
                raise RuntimeError(GoogleLLMLog.API_KEY_INVALID.value) from e
            raise RuntimeError(GoogleLLMLog.RUNTIME_GEN_ERROR.value + f": {e}") from e

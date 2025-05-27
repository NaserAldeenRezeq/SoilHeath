"""
google_llm.py

This module defines the `GoogleLLM` class, which provides an interface
for interacting with the Google Generative AI API while implementing
the ILLMsGenerators abstract base class.
"""

import os
import sys
import logging
from typing import Optional, Any
import google.generativeai as genai
from google.api_core import exceptions # Import exceptions for API errors

# --- Setup for project-specific imports ---
# This block attempts to dynamically add the project root to sys.path
# It's crucial for `src.logs`, `src.helpers`, and `.abc_llm` to be found.
try:
    CURRENT_DIR = os.path.dirname(__file__)
    # Attempt to find the main project directory by going up one or two levels
    MAIN_DIR_CANDIDATES = [
        os.path.abspath(os.path.join(CURRENT_DIR, "../")),
        os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
    ]
    MAIN_DIR = None
    for candidate in MAIN_DIR_CANDIDATES:
        if os.path.exists(candidate):
            MAIN_DIR = candidate
            break

    if MAIN_DIR is None:
        raise FileNotFoundError(
            f"Project directory not found. Attempted: {MAIN_DIR_CANDIDATES}"
        )

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    # Import project-specific modules
    # Ensure these modules (logs, helpers, abc_llm) exist and are correctly structured
    from src.logs import log_error, log_info
    from src.helpers import get_settings, Settings
    from .abc_llm import ILLMsGenerators # Relative import for abc_llm

except ImportError as ie:
    # Catch specific ImportError for better debugging of missing modules
    logging.critical("Module import error in google_llm.py: %s", ie, exc_info=True)
    raise
except Exception as e:
    # Catch any other unexpected errors during initialization
    logging.critical("Initialization error in google_llm.py: %s", e, exc_info=True)
    raise


class GoogleLLM(ILLMsGenerators):
    """
    Implementation of ILLMsGenerators for Google's Generative AI models.
    """

    def __init__(
        self,
        model_name: str = "gemini-1.0-pro",
        max_new_tokens: int = 1024,
        do_sample: bool = True, # Kept for interface compatibility
        temperature: float = 0.5,
        top_p: float = 0.95,
        top_k: int = 50,
        trust_remote_code: bool = False, # Kept for interface compatibility
        quantization: bool = False, # Kept for interface compatibility
        quantization_type: str = "8bit", # Kept for interface compatibility
        **kwargs: Any # Use Any for kwargs for better type hinting
    ) -> None:
        """
        Initialize GoogleLLM with generation parameters.

        Note: Some parameters like trust_remote_code, quantization are kept for interface
        compatibility but aren't used with Google's API.
        """
        self.app_settings: Settings = get_settings() # Explicitly type app_settings
        self.model_name = "gemini-1.5-flash"
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.model: Optional[genai.GenerativeModel] = None # Type hint for model
        self.generation_config: Optional[genai.types.GenerationConfig] = None # Type hint

        # Log unused parameters for transparency and potential user awareness
        if not do_sample:
            log_info("Note: 'do_sample=False' is not directly configurable for sampling in Google Generative AI models via this API.")
        if trust_remote_code:
            log_info("Note: 'trust_remote_code' is not applicable to Google Generative AI API usage.")
        if quantization:
            log_info(f"Note: 'quantization' ({quantization_type}) is not directly configurable via this Google Generative AI API.")

        # Store any additional kwargs, though not directly used here, for potential future extensions
        self.additional_kwargs = kwargs

    def initialize_llm(self) -> None:
        """
        Configure the Google AI client and set generation parameters.
        This method should be called before attempting to generate responses.
        """
        try:
            api_key = self.app_settings.GOOGLE_API_KEY
            if not api_key:
                # Use a more specific exception for configuration errors
                raise ValueError("Google API key is missing in settings. Please ensure GOOGLE_API_KEY is set.")

            # Configure the genai library with the API key
            genai.configure(api_key=api_key)
            
            # Create the GenerationConfig instance
            self.generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k
            )
            
            # Initialize the GenerativeModel with the correctly formatted model name
            self.model = genai.GenerativeModel(self.model_name)
            
            log_info(f"GoogleLLM initialized successfully with model: '{self.model_name}'")
            log_info(f"Generation config applied: {self.generation_config}")

        except ValueError as ve:
            # Catch specific ValueError for missing API key
            log_error(f"Configuration error during GoogleLLM initialization: {ve}")
            raise RuntimeError(f"GoogleLLM initialization failed: {ve}") from ve
        except Exception as e:
            # Catch any other unexpected errors during initialization
            log_error(f"An unexpected error occurred during GoogleLLM initialization: {e}")
            raise RuntimeError(f"GoogleLLM initialization failed due to an unexpected error: {e}") from e

    def response(self, prompt: str) -> str:
        """
        Generate a response from the Google model.

        Args:
            prompt: Input text to generate response for

        Returns:
            Generated response text

        Raises:
            RuntimeError: If generation fails or model not initialized
            ValueError: If the prompt is empty or invalid
        """
        # Ensure the model and config are initialized before attempting to generate
        if self.model is None or self.generation_config is None:
            log_error("GoogleLLM is not initialized. Call initialize_llm() first.")
            raise RuntimeError("GoogleLLM not properly initialized. Call initialize_llm() before generating content.")
        
        if not prompt or not isinstance(prompt, str):
            log_error("Invalid prompt provided. Prompt must be a non-empty string.")
            raise ValueError("Prompt must be a non-empty string.")

        try:
            # Call the generate_content method with the prompt and generation config
            # Using a list for the prompt is generally more robust for future multi-turn support
            # and aligns with how chat models expect input.
            response = self.model.generate_content(
                [prompt], # Wrap prompt in a list for consistency
                generation_config=self.generation_config
            )

            # Check if candidates exist and if the first candidate has content
            if response and response.candidates:
                # Access the text from the first part of the first candidate
                # This handles cases where content might be structured differently (e.g., with parts)
                generated_text = ""
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        generated_text += part.text
                return generated_text.strip()
            else:
                # Handle cases where no candidates or no content is returned
                log_error(f"Google API returned an empty or invalid response for prompt: {prompt[:100]}...")
                raise RuntimeError("Google API returned an empty or invalid response. No content generated.")

        except exceptions.GoogleAPICallError as api_err: # Changed from genai.types.APIError
            # Specific handling for API errors (e.g., invalid key, rate limits, model not found)
            log_error(f"Google API error during generation: {api_err}")
            raise RuntimeError(f"Google API error during text generation: {api_err}") from api_err
        except Exception as e:
            # Catch any other unexpected errors during generation
            log_error(f"An unexpected error occurred during text generation for prompt: {prompt[:100]}... Error: {e}")
            raise RuntimeError(f"Text generation failed due to an unexpected error: {e}") from e

    def __call__(self, prompt: str) -> str:
        """
        Makes the GoogleLLM instance callable directly, acting as a shortcut for response().
        """
        return self.response(prompt)

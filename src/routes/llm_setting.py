"""
Here Docstirn
"""
import os
import sys
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR



try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.llm import HuggingFaceLLM, GoogleLLM
    from src.schemes import LLMsSettings
except (ValueError, ImportError, AttributeError) as e:
    raise ImportError(f"[IMPORT ERROR]: {e}") from e

llm_settings_route = APIRouter()

@llm_settings_route.post("/llmsettings")
async def apply_model_settings(
    request: Request,
    body: LLMsSettings,
) -> JSONResponse:
    """
    Initialize and apply configuration to either a HuggingFace or Google model.
    """
    llm_name = body.llm_name
    try:
        common_config = {
            "max_new_tokens": body.max_new_tokens,
            "temperature": body.temperature,
            "top_p": body.top_p,
            "top_k": body.top_k,
        }

        if llm_name == "huggingface":
            model_config = {
                **common_config,
                "trust_remote_code": body.trust_remote_code,
                "do_sample": body.do_sample,
                "quantization": body.quantization,
                "quantization_type": body.quantization_type,
            }
            llm = HuggingFaceLLM(model_name=body.model_name, **model_config)
        elif llm_name == "google":
            model_config = {
                **common_config,
                # Add Google-specific parameters here if needed
            }
            llm = GoogleLLM(model_name=body.model_name, **model_config)
        else:
            raise ValueError(f"Unsupported model provider: {llm_name}")

        llm.initialize_llm()
        request.app.state.llm = llm

        message = f"[APPLICATION] {llm_name} model '{body.model_name}' initialized successfully."
        log_info(message)
        return JSONResponse(
            content={"message": message},
            status_code=HTTP_200_OK
        )

    except (ValueError, ImportError, AttributeError, RuntimeError) as e:
        error_message = f"[APPLICATION ERROR] Model '{body.model_name}' failed to initialize: {e}"
        log_error(error_message)
        return JSONResponse(
            content={"error": f"Failed to initialize model: {str(e)}"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )

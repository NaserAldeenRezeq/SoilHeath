from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from typing import Optional
import os
import sys

FILE_LOCATION = os.path.join(os.path.dirname(__file__), "llms.py")

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from llm import HuggingFaceLLM
    from schemes import LLMsSettings
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {FILE_LOCATION}: {e}")

llm_settings_route = APIRouter()

@llm_settings_route.post("/llmsettings")
async def apply_model_settings(
    request: Request,
    body: LLMsSettings,
) -> JSONResponse:
    """
    Initialize and apply configuration to a HuggingFace model.
    """
    try:
        model_config = {
            "max_new_tokens": body.max_new_tokens,
            "temperature": body.temperature,
            "top_p": body.top_p,
            "top_k": body.top_k,
            "trust_remote_code": body.trust_remote_code,
            "do_sample": body.do_sample,
            "quantization": body.quantization,
            "quantization_type": body.quantization_type,
        }

        hf_llm = HuggingFaceLLM(model_name=body.model_name, **model_config)
        hf_llm.initialize_llm()
        request.app.state.llm = hf_llm

        message = f"[APPLICATION] Model '{body.model_name}' initialized successfully."
        log_info(message)
        return JSONResponse(
            content={"message": message},
            status_code=HTTP_200_OK
        )

    except Exception as e:
        error_message = f"[APPLICATION ERROR] Model '{body.model_name}' failed to initialize: {e}"
        log_error(error_message)
        return JSONResponse(
            content={"error": f"Failed to initialize model: {str(e)}"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
from pydantic import BaseModel
from typing import Optional, Literal

class LLMsSettings(BaseModel):
    llm_name: str
    model_name: str
    max_new_tokens: int
    temperature: float
    top_p: float
    top_k: int
    trust_remote_code: bool
    do_sample: bool
    quantization: bool
    quantization_type: Optional[Literal["4bit", "8bit"]] = None

from typing import Callable
from .azure_openai import call_azure_openai_api
from .chutes import call_chutes_model_api
from .gemini import call_gemini_api

def get_llm_api_call_function(prompt_text,model_name: str) -> Callable:
    """
    Returns the appropriate LLM API call function based on the model name.
    """
    if model_name.lower() == "azure":
        return call_azure_openai_api(prompt_text)
    elif model_name.lower() == "chutes":
        return call_chutes_model_api(prompt_text)
    elif model_name.lower() == "gemini":
        return call_gemini_api(prompt_text)
    else:
        raise ValueError(f"Unsupported LLM model: {model_name}")

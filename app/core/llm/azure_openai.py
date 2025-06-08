import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_API_BASE_URL = os.getenv("AZURE_OPENAI_ENDPOINT")  # Example: "https://your-endpoint.openai.azure.com/"
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # Example: "gpt-4-1"
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-12-01-preview")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

def get_azure_api_key():
    """
    Get Azure OpenAI API key from environment variable.
    """
    if not AZURE_API_KEY:
        print("Error: AZURE_OPENAI_API_KEY is not set.")
    return AZURE_API_KEY

def call_azure_openai_api(prompt_text):
    """
    Calls Azure OpenAI Chat Completion endpoint synchronously.
    
    Args:
        prompt_text (str): The user prompt for the assistant.

    Returns:
        str: The assistant's response, or an error message.
    """
    api_key = get_azure_api_key()
    if not api_key:
        return "Error: API Key not found."

    if not AZURE_API_BASE_URL or not AZURE_DEPLOYMENT_NAME:
        return "Error: Missing AZURE_OPENAI_ENDPOINT or AZURE_DEPLOYMENT_NAME."

    url = f"{AZURE_API_BASE_URL}openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={AZURE_API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 4096,
        "temperature": 1.0,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

    try:
        print(f"Calling Azure OpenAI at {url}...")
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        response_json = response.json()

        if (
            "choices" in response_json and
            isinstance(response_json["choices"], list) and
            len(response_json["choices"]) > 0 and
            "message" in response_json["choices"][0] and
            "content" in response_json["choices"][0]["message"]
        ):
            return response_json["choices"][0]["message"]["content"]

        print("Error: Unexpected response format.")
        return json.dumps(response_json, indent=2)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        try:
            return json.dumps(http_err.response.json(), indent=2)
        except Exception:
            return f"HTTP Error: {http_err.response.status_code} - {http_err.response.text}"

    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        return f"Request Exception: {err}"
    except json.JSONDecodeError as json_err:
        return f"JSON Decode Error: {json_err}"
    except Exception as e:
        return f"Unexpected Error: {e}"

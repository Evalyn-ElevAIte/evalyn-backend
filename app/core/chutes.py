"""
For calling the chutes API
This module provides functions to interact with the chutes API.
"""

import os
import requests  # For synchronous HTTP requests
import json      # Used for working with JSON data
from dotenv import load_dotenv  # For loading environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
CHUTES_API_ENDPOINT = "https://llm.chutes.ai/v1/chat/completions"
# API_KEY_ENV_VARIABLE = os.getenv("CHUTES_API_TOKEN") # This line assigns the key itself, not the var name

def get_chutes_api_key():
    """
    Retrieves the Chutes API key from an environment variable.

    Returns:
        str: The API key if found, otherwise None.
    """
    api_key = os.getenv("CHUTES_API_TOKEN")
    if not api_key:
        print("Error: The environment variable CHUTES_API_TOKEN is not set.")
        print("Please set it in your .env file or environment.")
        print("Example: CHUTES_API_TOKEN='your_actual_chutes_api_key_here'")
    return api_key

def call_chutes_model_api(prompt_text): # Removed api_key, will call get_chutes_api_key inside
    """
    Calls the Chutes model API synchronously with the given API key and prompt,
    and streams the response.

    Args:
        prompt_text (str): The prompt to send to the model.

    Returns:
        str: A string containing the concatenated streamed content if successful,
             or an error message string.
    """
    api_key = get_chutes_api_key()
    if not api_key:
        return "Error: Chutes API Key not found. Please ensure CHUTES_API_TOKEN is set."

    if not CHUTES_API_ENDPOINT:
        print("Error: CHUTES_API_ENDPOINT is not configured.")
        return "Error: CHUTES_API_ENDPOINT is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
      "model": "deepseek-ai/DeepSeek-R1",
      "messages": [{"role": "user", "content": prompt_text}],
      "stream": True,
      "max_tokens": 2048, # Increased for potentially longer analysis
      "temperature": 0.7
    }

    print(f"Streaming response from {CHUTES_API_ENDPOINT}...")
    
    accumulated_response_parts = []

    try:
        with requests.post(
            CHUTES_API_ENDPOINT,
            headers=headers,
            json=body,
            stream=True, # Enable streaming for requests library
            timeout=180  # 3 minute timeout for the entire request
        ) as response:
            # Check for HTTP errors
            response.raise_for_status() # Will raise an HTTPError for bad responses (4xx or 5xx)

            print("--- Model Stream ---")
            for line_bytes in response.iter_lines(): # Iterate over lines in the stream
                if line_bytes:
                    line = line_bytes.decode("utf-8").strip()
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            print("\n--- Stream [DONE] ---")
                            break
                        if data_str:
                            try:
                                chunk_json = json.loads(data_str)
                                # Attempt to extract meaningful content from the chunk.
                                # The exact structure depends on the Chutes API's streaming format.
                                # Common patterns involve a "choices" array, then "delta" or "message", then "content".
                                content_part = ""
                                if "choices" in chunk_json and isinstance(chunk_json["choices"], list) and chunk_json["choices"]:
                                    choice = chunk_json["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        content_part = choice["delta"]["content"]
                                    elif "message" in choice and "content" in choice["message"]: # Some APIs use this
                                        content_part = choice["message"]["content"]
                                
                                if content_part:
                                    print(content_part, end="", flush=True)
                                    accumulated_response_parts.append(content_part)
                                # else:
                                    # Optionally print the whole chunk if no specific content found, for debugging
                                    # print(f"\n[Debug Chunk]: {json.dumps(chunk_json, indent=2)}")

                            except json.JSONDecodeError:
                                print(f"\nError parsing JSON chunk: {data_str}")
                            except Exception as e:
                                print(f"\nError processing chunk: {data_str}, Error: {e}")
            print() # Newline after stream finishes
            
            return "".join(accumulated_response_parts) if accumulated_response_parts else "Stream completed, but no content was accumulated."

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err}"
        try:
            error_response_content = http_err.response.json()
            error_message += f" - Response: {json.dumps(error_response_content)}"
        except json.JSONDecodeError:
            error_message += f" - Response: {http_err.response.text}"
        print(error_message)
        return error_message
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection Error: {conn_err}")
        return f"Connection Error: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout Error: {timeout_err}")
        return f"Timeout Error: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred with the request: {req_err}")
        return f"Request Error: {req_err}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Unexpected Error: {e}"
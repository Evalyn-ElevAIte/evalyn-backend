import os
import requests # For synchronous HTTP requests
import json     # Used for working with JSON data
from dotenv import load_dotenv

# --- Configuration ---

load_dotenv() # Loads environment variables from .env file

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def get_api_key():
    """
    Retrieves the Gemini API key from an environment variable.

    Returns:
        str: The API key if found, otherwise None.
    """
    api_key = os.getenv("GEMINI_API_KEY") # Directly get the key
    if not api_key:
        print("Error: The environment variable GEMINI_API_KEY is not set.")
        print("Please set it in your .env file or environment.")
        print("Example: GEMINI_API_KEY='your_actual_gemini_api_key_here'")
    return api_key

def call_gemini_api(prompt_text): # Removed api_key from params, will call get_api_key inside
    """
    Calls the Gemini API synchronously with the API key (retrieved from env) and prompt.
    This version uses the non-streaming generateContent method.

    Args:
        prompt_text (str): The prompt to send to the model.

    Returns:
        str: The model's generated text if successful, otherwise None.
    """
    api_key = get_api_key() # Get API key
    if not api_key:
        return "Error: API Key not found. Please ensure GEMINI_API_KEY is set."

    if not GEMINI_API_BASE_URL:
        print("Error: GEMINI_API_BASE_URL is not configured.")
        return None # Or raise an error

    # Construct the full API URL with the API key
    api_url = f"{GEMINI_API_BASE_URL}?key={api_key}"

    # Define the headers for the API request
    headers = {
        "Content-Type": "application/json"
    }

    # Define the payload (body) for the Gemini API
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt_text}]
        }],
        # Optional: Add generationConfig if needed
        "generationConfig": {
           "temperature": 0.7, # Example temperature
           "maxOutputTokens": 4096
        }
    }

    print(f"Sending prompt to Gemini API at {GEMINI_API_BASE_URL}...")

    try:
        # Make the POST request using the requests library
        response = requests.post(api_url, headers=headers, json=payload, timeout=180) # 3 minute timeout

        # Raise an exception for HTTP errors (4xx or 5xx)
        response.raise_for_status()

        response_json = response.json() # Get JSON response

        # Process the successful response
        # Extract the generated text from the response
        if (response_json.get("candidates") and
                isinstance(response_json["candidates"], list) and
                len(response_json["candidates"]) > 0 and
                response_json["candidates"][0].get("content") and
                response_json["candidates"][0]["content"].get("parts") and
                isinstance(response_json["candidates"][0]["content"]["parts"], list) and
                len(response_json["candidates"][0]["content"]["parts"]) > 0 and
                response_json["candidates"][0]["content"]["parts"][0].get("text")):
            
            generated_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            return generated_text
        else:
            # Check for promptFeedback if no candidates are found
            if response_json.get("promptFeedback"):
                error_detail = f"Prompt Feedback: {json.dumps(response_json['promptFeedback'], indent=2)}"
                print(f"API call was successful but no content generated. {error_detail}")
                return f"Error: No content generated. {error_detail}"
            
            print("Error: Could not find generated text in the API response structure.")
            print(f"Full response: {json.dumps(response_json, indent=2)}")
            return "Error: Could not parse generated text from API response."

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        try:
            error_response_content = http_err.response.json()
            print(f"Error Response: {json.dumps(error_response_content, indent=2)}")
            return f"HTTP Error: {http_err.response.status_code} - {json.dumps(error_response_content)}"
        except json.JSONDecodeError:
            print(f"Error Response (not JSON): {http_err.response.text}")
            return f"HTTP Error: {http_err.response.status_code} - {http_err.response.text}"
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error Connecting: {conn_err}")
        return f"Connection Error: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout Error: {timeout_err}")
        return f"Timeout Error: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred with the request: {req_err}")
        return f"Request Error: {req_err}"
    except json.JSONDecodeError as json_err:
        # This would typically be caught by response.json() if the response isn't valid JSON
        print(f"JSON Decode Error: {json_err}. Response text: {response.text if 'response' in locals() else 'N/A'}")
        return f"JSON Decode Error: Failed to parse API response. {json_err}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Unexpected Error: {e}"
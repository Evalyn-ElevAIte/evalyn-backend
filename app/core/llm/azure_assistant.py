import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file if present
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Initialize client at module level
client = None
if AZURE_OPENAI_ENDPOINT and AZURE_API_KEY:
    try:
        client = AzureOpenAI(
            api_key=AZURE_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )
        print("Azure OpenAI client initialized in assistant_config.")
    except Exception as e:
        print(f"Error initializing Azure OpenAI client in assistant_config: {e}")
        client = None

# Shared state for assistant details (for simplicity in this example)
assistant_details = {
    "assistant_id": None,
    "thread_id": None,
    "vector_store_id": None,
    "file_ids_in_store": [],
    "openai_file_id_map": {},  # To map OpenAI file IDs to original filenames
}

def initialize_openai_client():
    """Initializes the Azure OpenAI client (legacy function, client now initialized at module level)."""
    global client
    if client is None and AZURE_OPENAI_ENDPOINT and AZURE_API_KEY:
        try:
            client = AzureOpenAI(
                api_key=AZURE_API_KEY,
                api_version=AZURE_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
            )
            print("Azure OpenAI client initialized in assistant_config.")
        except Exception as e:
            print(f"Error initializing Azure OpenAI client in assistant_config: {e}")
            client = None

__all__ = ["client", "assistant_details", "AZURE_OPENAI_DEPLOYMENT_NAME", "initialize_openai_client"]

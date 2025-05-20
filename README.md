# Evalyn Backend

This is the backend for the Evalyn project.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd evalyn-backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   On Windows:

        ```bash
        venv\Scripts\activate
        ```

    *   On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:**

    Copy the `.env.example` file and rename it to `.env`. Update the placeholder values with your actual credentials.

    ```bash
    cp .env.example .env
    ```

    or on Windows:

    ```bash
    copy .env.example .env
    ```

6.  **Run the application:**

    ```bash
    uvicorn main:app --reload
    ```

## Environment Variables

The application uses the following environment variables, which should be configured in the `.env` file:

*   `AZURE_OPENAI_API_KEY`: Your Azure OpenAI Service API key.
*   `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI Service endpoint URL.
*   `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your Azure OpenAI Service deployment.
*   `CHUTES_API_TOKEN`: Your API token for the Chutes service.
*   `GEMINI_API_KEY`: Your API key for the Gemini service.

## Dependencies

The project dependencies are listed in the `requirements.txt` file. Key dependencies include:

*   `fastapi`: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   `python-dotenv`: Reads key-value pairs from a `.env` file and can set them as environment variables.
*   `openai`: The official Python library for the OpenAI API.
*   `pydantic`: Data validation and settings management using Python type annotations.
*   `uvicorn`: An ASGI server implementation, for running FastAPI applications.
*   `aiohttp`: An asynchronous HTTP client/server framework for asyncio and Python.
*   `requests`: An elegant and simple HTTP library for Python.

## Project Structure

(Add details about the project structure here)

## Contributing

(Add contributing guidelines here)

## License

(Add license information here)

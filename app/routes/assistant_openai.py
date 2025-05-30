import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Form,APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.llm.azure_assistant import initialize_openai_client, assistant_details, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME, client as openai_client
from app.services.assistant_service import setup_assistant_resources, process_chat_message


router = APIRouter()

# @router.get("/", response_class=HTMLResponse)
# async def read_root():
#     """Serves the main HTML page for the chatbot."""
#     if not openai_client:
#         # A simple HTML response if client isn't initialized
#         return HTMLResponse(content="<html><body><h1>Error</h1><p>Azure OpenAI client not initialized. Please check server logs and environment variables (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL_DEPLOYMENT_NAME).</p></body></html>", status_code=503)
#     return HTMLResponse(content=get_html_page())

@router.post("/setup_assistant_and_thread")
async def handle_setup_assistant_and_thread(pdfFile: UploadFile = File(...)):
    """
    Handles PDF upload, creates an assistant with file_search tool,
    a vector store with the file, and a new thread.
    """
    if not openai_client:
        raise HTTPException(status_code=503, detail="Azure OpenAI client not initialized. Check server logs.")

    if not pdfFile.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    try:
        contents = await pdfFile.read() # Read file content
        # Call the logic function to handle the setup
        result = await setup_assistant_resources(
            file_content=contents,
            filename=pdfFile.filename,
            assistant_config=assistant_details # Pass the shared state
        )
        return JSONResponse(content=result)
    except HTTPException as http_exc: # Re-raise FastAPI's own exceptions
        raise http_exc
    except Exception as e:
        print(f"Error in /setup_assistant_and_thread: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during setup: {str(e)}")

@router.post("/chat")
async def handle_chat_with_assistant(request: Request):
    """Handles a user message, runs the assistant, and returns the reply."""
    if not openai_client:
        raise HTTPException(status_code=503, detail="Azure OpenAI client not initialized. Check server logs.")

    try:
        data = await request.json()
        user_message_content = data.get('user_message')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    if not user_message_content:
        raise HTTPException(status_code=400, detail="No message content provided ('user_message' field missing).")

    # Retrieve stored IDs from the shared state
    thread_id = assistant_details.get("thread_id")
    assistant_id = assistant_details.get("assistant_id")

    if not thread_id or not assistant_id:
        raise HTTPException(status_code=400, detail="Assistant or thread not initialized. Please upload a PDF first via /setup_assistant_and_thread.")

    try:
        # Call the logic function to handle the chat message
        response_data = await process_chat_message(
            user_message=user_message_content,
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        return JSONResponse(content=response_data)
    except HTTPException as http_exc: # Re-raise FastAPI's own exceptions
        raise http_exc
    except Exception as e:
        print(f"Error in /chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during chat: {str(e)}")
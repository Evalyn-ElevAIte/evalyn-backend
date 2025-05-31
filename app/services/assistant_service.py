import time
import io  # For BytesIO
import logging
from openai import APIError  # Import APIError from openai directly
from app.core.llm.azure_assistant import (
    client as openai_client_func,
    assistant_details,
    AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_openai_client():
    """Get the OpenAI client instance"""
    try:
        # If client is a function, call it to get the actual client
        if callable(openai_client_func):
            return openai_client_func()
        # If client is already an instance, return it directly
        else:
            return openai_client_func
    except Exception as e:
        logger.error(f"Failed to get OpenAI client: {e}")
        return None


async def setup_assistant_resources(
    file_content: bytes, filename: str, assistant_config: dict
):
    """
    Sets up OpenAI resources: uploads file, creates vector store, assistant, and thread.
    Manages state in the passed assistant_config dictionary.
    """
    openai_client = get_openai_client()

    if not openai_client:
        raise Exception("OpenAI client not initialized.")

    # Initialize the openai_file_id_map if it doesn't exist
    if "openai_file_id_map" not in assistant_config:
        assistant_config["openai_file_id_map"] = {}

    try:
        # 1. Upload file to OpenAI
        logger.info("Uploading file to OpenAI...")
        # Use BytesIO to treat bytes as a file-like object
        file_like_object = io.BytesIO(file_content)
        file_like_object.name = filename  # OpenAI SDK might use the .name attribute

        openai_file = openai_client.files.create(
            file=file_like_object, purpose="assistants"
        )
        logger.info(f"File '{filename}' uploaded to OpenAI. File ID: {openai_file.id}")
        assistant_config["openai_file_id_map"][openai_file.id] = filename

        # 2. Create a Vector Store if it doesn't exist or needs to be fresh
        # For simplicity, we create a new one each time. In a real app, you might reuse or update.
        if assistant_config.get("vector_store_id"):
            try:
                logger.info(
                    f"Attempting to delete old vector store: {assistant_config['vector_store_id']}"
                )
                openai_client.vector_stores.delete(
                    vector_store_id=assistant_config["vector_store_id"]
                )
                logger.info(
                    f"Old vector store {assistant_config['vector_store_id']} deleted."
                )
            except Exception as e:
                logger.warning(
                    f"Could not delete old vector store {assistant_config.get('vector_store_id')}: {e}"
                )

        logger.info("Creating new vector store...")
        vector_store = openai_client.vector_stores.create(
            name=f"QuizDocs_{filename.split('.')[0]}_{int(time.time())}",
            # expires_after={"anchor": "last_active_at", "days": 1} # Optional: auto-delete
        )
        assistant_config["vector_store_id"] = vector_store.id
        logger.info(f"Vector store created. ID: {vector_store.id}")

        # 3. Add the file to the Vector Store
        logger.info(
            f"Adding file {openai_file.id} to vector store {vector_store.id}..."
        )
        file_batch = openai_client.vector_stores.file_batches.create_and_poll(
            vector_store_id=vector_store.id, file_ids=[openai_file.id]
        )
        logger.info(f"File batch processing status: {file_batch.status}")

        if file_batch.status == "completed":
            # Verify files in store
            vs_files = openai_client.vector_stores.files.list(
                vector_store_id=vector_store.id
            )
            assistant_config["file_ids_in_store"] = [f.id for f in vs_files.data]
            logger.info(
                f"Files confirmed in vector store: {assistant_config['file_ids_in_store']}"
            )
        else:
            # Attempt to clean up if file batch failed
            try:
                openai_client.vector_stores.delete(vector_store_id=vector_store.id)
            except:
                pass
            try:
                openai_client.files.delete(file_id=openai_file.id)
            except:
                pass
            raise Exception(
                f"Failed to add file to vector store. Status: {file_batch.status}. Cleaned up resources."
            )

        # 4. Create or Update Assistant
        assistant_instructions = (
            "You are an expert assistant lecturer. Your primary role is to help lecturers "
            "discuss and create effective quizzes and assessment materials. "
            "You should use the content from the provided PDF document(s) to answer questions, "
            "suggest quiz questions, explain concepts relevant to quiz topics, and help structure quizzes. "
            "When referring to the document, be specific if possible by citing the source file. Always be helpful, polite, and focus on educational best practices."
        )

        # For simplicity, create a new assistant each time.
        # Alternatively, you could update an existing one if assistant_config["assistant_id"] exists.
        if assistant_config.get("assistant_id"):
            try:
                logger.info(
                    f"Attempting to delete old assistant: {assistant_config['assistant_id']}"
                )
                openai_client.assistants.delete(
                    assistant_id=assistant_config["assistant_id"]
                )
                logger.info(
                    f"Old assistant {assistant_config['assistant_id']} deleted."
                )
            except Exception as e:
                logger.warning(
                    f"Could not delete old assistant {assistant_config.get('assistant_id')}: {e}"
                )

        logger.info("Creating new assistant...")
        assistant = openai_client.beta.assistants.create(
            name="FastAPILecturerQuizHelper",
            instructions=assistant_instructions,
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        assistant_config["assistant_id"] = assistant.id
        logger.info(f"Assistant created. ID: {assistant.id}")

        # 5. Create a new Thread for the new session
        if assistant_config.get("thread_id"):
            try:
                logger.info(
                    f"Attempting to delete old thread: {assistant_config['thread_id']}"
                )
                openai_client.threads.delete(
                    thread_id=assistant_config["thread_id"]
                )
                logger.info(f"Old thread {assistant_config['thread_id']} deleted.")
            except Exception as e:
                logger.warning(
                    f"Could not delete old thread {assistant_config.get('thread_id')}: {e}"
                )

        logger.info("Creating new thread...")
        thread = openai_client.beta.threads.create()
        assistant_config["thread_id"] = thread.id
        logger.info(f"Thread created. ID: {thread.id}")

        return {
            "message": "Assistant, vector store, and thread configured successfully with the new PDF.",
            "assistant_id": assistant.id,
            "thread_id": thread.id,
            "vector_store_id": vector_store.id,
            "openai_file_id": openai_file.id,
            "original_filename": filename,
            "files_in_vector_store": assistant_config["file_ids_in_store"],
        }

    except APIError as e:
        logger.error(f"Azure OpenAI API Error during setup: {e}")
        # Attempt to clean up resources if an error occurs mid-way
        if assistant_config.get("vector_store_id"):
            try:
                openai_client.vector_stores.delete(
                    vector_store_id=assistant_config["vector_store_id"]
                )
            except:
                pass
        if (
            "openai_file" in locals() and openai_file
        ):  # Check if openai_file was defined
            try:
                openai_client.files.delete(file_id=openai_file.id)
            except:
                pass
        raise Exception(
            f"Azure OpenAI API Error: {e.message if hasattr(e, 'message') else str(e)}"
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during setup: {e}")
        raise Exception(f"An unexpected error occurred: {str(e)}")


async def process_chat_message(user_message: str, thread_id: str, assistant_id: str):
    """
    Adds a message to a thread, runs the assistant, and retrieves the reply.
    Uses manual polling approach as shown in your example.
    """
    openai_client = get_openai_client()

    if not openai_client:
        raise Exception("OpenAI client not initialized.")

    try:
        # 1. Add message to the thread
        logger.info(f"Adding message to thread {thread_id}: '{user_message}'")
        message = openai_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )

        # 2. Create a Run (not create_and_poll)
        logger.info(f"Creating run for assistant {assistant_id} on thread {thread_id}")
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        logger.info(f"Run created. ID: {run.id}, Status: {run.status}")

        # 3. Manual polling until the run completes or fails
        max_wait_time = 60  # Maximum wait time in seconds
        start_time = time.time()

        while run.status in ["queued", "in_progress", "cancelling"]:
            # Check if we've exceeded maximum wait time
            if time.time() - start_time > max_wait_time:
                logger.error(f"Run timed out after {max_wait_time} seconds")
                raise Exception(
                    f"Assistant run timed out after {max_wait_time} seconds"
                )

            time.sleep(1)  # Wait 1 second before checking again
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )
            logger.debug(f"Run status: {run.status}")

        # 4. Handle the completed run
        if run.status == "completed":
            # Get the messages from the thread
            messages = openai_client.beta.threads.messages.list(
                thread_id=thread_id, order="desc"  # Get newest messages first
            )

            # Find the assistant's response
            assistant_reply_content = None
            for msg in messages.data:
                if msg.run_id == run.id and msg.role == "assistant":
                    if msg.content and len(msg.content) > 0:
                        text_content_item = msg.content[0]
                        if text_content_item.type == "text":
                            assistant_reply_content = text_content_item.text.value

                            # Handle annotations (file citations)
                            annotations = text_content_item.text.annotations
                            if annotations:
                                for annotation in annotations:
                                    if annotation.type == "file_citation":
                                        cited_file_id = annotation.file_citation.file_id
                                        # Use the map from assistant_config if available
                                        original_filename = assistant_details.get(
                                            "openai_file_id_map", {}
                                        ).get(cited_file_id, cited_file_id)
                                        citation_text = f"[Source: {original_filename}]"
                                        assistant_reply_content = (
                                            assistant_reply_content.replace(
                                                annotation.text, citation_text
                                            )
                                        )
                            break

            if assistant_reply_content:
                logger.info(f"Assistant reply received successfully")
                return {"assistant_reply": assistant_reply_content}
            else:
                return {
                    "assistant_reply": "Assistant processed the request but provided no textual reply."
                }

        elif run.status == "requires_action":
            # Handle tool calls if needed
            logger.warning(f"Run requires action: {run.required_action}")
            raise Exception(
                "Run requires further action (e.g. tool calls), which is not fully implemented for automatic handling in this example."
            )

        else:
            # Handle failed, cancelled, expired, etc.
            error_message = (
                f"Assistant run did not complete successfully. Status: {run.status}"
            )
            if run.last_error:
                error_message = f"Run failed: {run.last_error.message} (Code: {run.last_error.code})"
            elif hasattr(run, "incomplete_details") and run.incomplete_details:
                error_message = f"Run incomplete: {run.incomplete_details.reason}"

            logger.error(error_message)
            raise Exception(error_message)

    except APIError as e:
        logger.error(f"Azure OpenAI API Error during chat: {e}")
        raise Exception(
            f"Azure OpenAI API Error: {e.message if hasattr(e, 'message') else str(e)}"
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during chat: {e}")
        import traceback

        traceback.print_exc()
        raise Exception(f"An unexpected error occurred: {str(e)}")


def process_chat_message_sync(user_message: str, thread_id: str, assistant_id: str):
    """
    Synchronous version of process_chat_message for use with Streamlit.
    """
    openai_client = get_openai_client()

    if not openai_client:
        raise Exception("OpenAI client not initialized.")

    try:
        # 1. Add message to the thread
        logger.info(f"Adding message to thread {thread_id}: '{user_message}'")
        message = openai_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )

        # 2. Create a Run
        logger.info(f"Creating run for assistant {assistant_id} on thread {thread_id}")
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

        # 3. Manual polling
        max_wait_time = 60
        start_time = time.time()

        while run.status in ["queued", "in_progress", "cancelling"]:
            if time.time() - start_time > max_wait_time:
                raise Exception(
                    f"Assistant run timed out after {max_wait_time} seconds"
                )

            time.sleep(1)
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

        # 4. Handle completed run
        if run.status == "completed":
            messages = openai_client.beta.threads.messages.list(
                thread_id=thread_id, order="desc"
            )

            assistant_reply_content = None
            for msg in messages.data:
                if msg.run_id == run.id and msg.role == "assistant":
                    if msg.content and len(msg.content) > 0:
                        text_content_item = msg.content[0]
                        if text_content_item.type == "text":
                            assistant_reply_content = text_content_item.text.value

                            # Handle annotations
                            annotations = text_content_item.text.annotations
                            if annotations:
                                for annotation in annotations:
                                    if annotation.type == "file_citation":
                                        cited_file_id = annotation.file_citation.file_id
                                        original_filename = assistant_details.get(
                                            "openai_file_id_map", {}
                                        ).get(cited_file_id, cited_file_id)
                                        citation_text = f"[Source: {original_filename}]"
                                        assistant_reply_content = (
                                            assistant_reply_content.replace(
                                                annotation.text, citation_text
                                            )
                                        )
                            break

            if assistant_reply_content:
                return {"assistant_reply": assistant_reply_content}
            else:
                return {
                    "assistant_reply": "Assistant processed the request but provided no textual reply."
                }

        else:
            error_message = f"Assistant run failed with status: {run.status}"
            if run.last_error:
                error_message = f"Run failed: {run.last_error.message}"
            raise Exception(error_message)

    except Exception as e:
        logger.error(f"Error in sync chat: {e}")
        raise Exception(f"Chat error: {str(e)}")

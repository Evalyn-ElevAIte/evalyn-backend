import streamlit as st
import requests
import time
import io
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api"  # Adjust this to your FastAPI server URL
SETUP_ENDPOINT = f"{API_BASE_URL}/assistant/setup_assistant_and_thread"
CHAT_ENDPOINT = f"{API_BASE_URL}/assistant/chat"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assistant_initialized" not in st.session_state:
    st.session_state.assistant_initialized = False
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

def upload_pdf_and_setup_assistant(pdf_file) -> bool:
    """Upload PDF and setup assistant through API"""
    try:
        with st.spinner("Setting up assistant with your PDF... This may take a moment."):
            # Prepare file for upload
            files = {"pdfFile": (pdf_file.name, pdf_file, "application/pdf")}
            
            # Make API call
            response = requests.post(SETUP_ENDPOINT, files=files, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Assistant setup successful!")
                st.success(f"📄 File: {result.get('original_filename')}")
                st.success(f"🤖 Assistant ID: {result.get('assistant_id')[:8]}...")
                st.success(f"💬 Thread ID: {result.get('thread_id')[:8]}...")
                return True
            else:
                st.error(f"❌ Setup failed: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The file might be too large or the server is busy.")
        return False
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the API server. Make sure your FastAPI server is running.")
        return False
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        return False

def send_message_to_assistant(message: str) -> Optional[str]:
    """Send message to assistant and get response"""
    try:
        with st.spinner("Assistant is thinking..."):
            payload = {"user_message": message}
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("assistant_reply", "No response received")
            else:
                st.error(f"❌ Chat failed: {response.text}")
                return None
                
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The assistant might be processing a complex request.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the API server.")
        return None
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(
    page_title="📚 Lecturer Quiz Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Lecturer Quiz Assistant")
st.markdown("Upload a PDF document and chat with your AI assistant to create quizzes and discuss educational content!")

# Sidebar for file upload and settings
with st.sidebar:
    st.header("📁 Document Upload")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document that the assistant will use to help create quizzes and answer questions."
    )
    
    if uploaded_file is not None:
        if not st.session_state.assistant_initialized or st.session_state.uploaded_file_name != uploaded_file.name:
            st.info(f"📄 Selected: {uploaded_file.name}")
            if st.button("🚀 Setup Assistant", type="primary"):
                if upload_pdf_and_setup_assistant(uploaded_file):
                    st.session_state.assistant_initialized = True
                    st.session_state.uploaded_file_name = uploaded_file.name
                    # Clear previous messages when new file is uploaded
                    st.session_state.messages = []
                    st.rerun()
        else:
            st.success(f"✅ Assistant ready with: {uploaded_file.name}")
    
    # Settings
    st.header("⚙️ Settings")
    st.info(f"🌐 API Server: {API_BASE_URL}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Assistant status
    st.header("🤖 Assistant Status")
    if st.session_state.assistant_initialized:
        st.success("✅ Ready")
    else:
        st.warning("⚠️ Not initialized")

# Main chat interface
if not st.session_state.assistant_initialized:
    st.info("👈 Please upload a PDF file and setup the assistant to start chatting!")
    
    # Show example questions
    st.markdown("### 💡 Example Questions You Can Ask:")
    st.markdown("""
    - "Create 5 multiple choice questions about chapter 3"
    - "What are the main topics covered in this document?"
    - "Generate a quiz with 10 questions covering the entire document"
    - "Explain the concept of [specific topic] from the document"
    - "Create true/false questions about [specific section]"
    - "What would be good essay questions for this material?"
    """)
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your document or request quiz questions..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        response = send_message_to_assistant(prompt)
        
        if response:
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            st.error("Failed to get response from assistant. Please try again.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🎓 Lecturer Quiz Assistant | Powered by Azure OpenAI Assistant API</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Additional features in expandable sections
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    1. **Upload a PDF**: Click "Choose a PDF file" in the sidebar and select your document
    2. **Setup Assistant**: Click "🚀 Setup Assistant" to initialize the AI with your document
    3. **Start Chatting**: Once setup is complete, ask questions about your document or request quiz creation
    4. **Get Responses**: The assistant will provide answers based on your uploaded document
    
    **Tips:**
    - Be specific in your questions for better results
    - Ask for different types of questions (multiple choice, true/false, essay, etc.)
    - Request quizzes for specific chapters or topics
    - The assistant can explain concepts from your document
    """)

with st.expander("🛠️ Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    - **Connection Error**: Make sure your FastAPI server is running on the correct port
    - **Upload Failed**: Check that your PDF file is not corrupted and is less than 20MB
    - **Slow Response**: Large documents may take longer to process
    - **No Response**: Try rephrasing your question or check the server logs
    
    **API Endpoints:**
    - Setup: `POST /assistant/setup_assistant_and_thread`
    - Chat: `POST /assistant/chat`
    """)

# Auto-refresh for real-time updates (optional)
if st.session_state.assistant_initialized:
    # You can add periodic checks here if needed
    pass
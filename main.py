import streamlit as st
from app.prompts.prompt_generator import construct_assignment_analysis_prompt
from app.core import gemini, chutes
import asyncio # Required if the underlying API calls use asyncio.run()

# --- Main Streamlit App ---
def run_streamlit_app():
    """
    Sets up and runs the Streamlit application for AI Assignment Analyzer.
    """
    st.set_page_config(page_title="AI Assignment Analyzer", layout="wide")

    st.title("📝 AI Assignment Analyzer")
    st.markdown("---")

    st.info("""
    **Instructions:**
    1.  Fill in all the details for the assignment below.
    2.  Select the AI Model you intend to use.
    3.  Click the "Analyze Assignment" button.
    4.  The AI model will evaluate the student's answer and provide feedback.
    """)
    st.markdown("---")

    # --- Model Selection ---
    st.sidebar.header("🤖 AI Model Selection")
    selected_model = st.sidebar.radio(
        "Choose the AI model to use for analysis:",
        ("Gemini", "Chutes"),
        key="model_selection"
    )
    st.sidebar.markdown(f"You have selected: **{selected_model}**")
    st.sidebar.markdown("---")
    # Add API Key input to sidebar if needed by your core functions
    # For example, if get_api_key() is not implemented in core modules:
    # gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password", key="gemini_key")
    # chutes_api_key = st.sidebar.text_input("Chutes API Key", type="password", key="chutes_key")


    # --- Input Columns for better layout ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Assignment Details")
        assignment_question = st.text_area(
            "Enter the full Assignment Question:",
            height=150,
            key="question",
            placeholder="e.g., Explain the process of cellular respiration and its significance."
        )

        st.subheader("Evaluation Metrics (from Lecturer)")
        st.caption("Enter each metric on a new line.")
        evaluation_metrics_input = st.text_area(
            "Metrics:",
            height=150,
            key="metrics",
            placeholder="e.g., Accurate definition of cellular respiration.\nIdentification of key stages (glycolysis, Krebs cycle, oxidative phosphorylation)."
        )

        st.subheader("Specific Contextual Requirements/Constraints")
        st.caption("Enter each requirement on a new line. (Optional)")
        contextual_requirements_input = st.text_area(
            "Requirements:",
            height=100,
            key="requirements",
            placeholder="e.g., Word count should be between 300-400 words.\nInclude at least one diagram."
        )

    with col2:
        st.header("2. Lecturer's Reference")
        lecturer_answer = st.text_area(
            "Enter the Lecturer's Ideal Answer or Key Points:",
            height=250,
            key="lecturer_answer",
            placeholder="Provide a comprehensive model answer or detailed key points the student should cover."
        )

        st.header("3. Student's Submission")
        student_answer = st.text_area(
            "Enter the Student's Submitted Answer:",
            height=250,
            key="student_answer",
            placeholder="Paste the student's full assignment submission here."
        )

    st.markdown("---")
    st.header("4. Analyze Assignment with AI Model")

    if 'analysis_response' not in st.session_state:
        st.session_state.analysis_response = None
    if 'generated_prompt' not in st.session_state:
        st.session_state.generated_prompt = None


    if st.button("🚀 Analyze Assignment", key="analyze_button", type="primary"):
        st.session_state.analysis_response = None # Reset previous response
        st.session_state.generated_prompt = None  # Reset previous prompt

        # Validate essential inputs
        required_fields = {
            "Assignment Question": assignment_question,
            "Evaluation Metrics": evaluation_metrics_input,
            "Lecturer's Ideal Answer/Key Points": lecturer_answer,
            "Student's Submitted Answer": student_answer
        }
        missing_fields = [name for name, value in required_fields.items() if not value]
        if missing_fields:
            st.error(f"⚠️ Please fill in the following required fields: {', '.join(missing_fields)}")
            return

        evaluation_metrics = [metric.strip() for metric in evaluation_metrics_input.split('\n') if metric.strip()]
        if not evaluation_metrics:
            st.error("⚠️ Please ensure at least one valid Evaluation Metric is provided.")
            return
        
        contextual_requirements = [req.strip() for req in contextual_requirements_input.split('\n') if req.strip()]

        st.info(f"⏳ Generating prompt and calling **{selected_model}** model... Please wait.")

        try:
            full_prompt = construct_assignment_analysis_prompt(
                assignment_question=assignment_question,
                evaluation_metrics=evaluation_metrics,
                contextual_requirements=contextual_requirements,
                lecturer_answer=lecturer_answer,
                student_answer=student_answer
            )
            st.session_state.generated_prompt = full_prompt
            
            api_response = None
            with st.spinner(f"🤖 Calling {selected_model} model... This may take a moment."):
                if selected_model == "Gemini":
                    # Ensure gemini.call_gemini_api is a synchronous wrapper or handles asyncio appropriately
                    # Pass API key if your function requires it, e.g., gemini.call_gemini_api(gemini_api_key, full_prompt)
                    api_response = gemini.call_gemini_api(full_prompt) 
                elif selected_model == "Chutes":
                    # Ensure chutes.call_chutes_model_api is a synchronous wrapper
                    # Pass API key if your function requires it, e.g., chutes.call_chutes_model_api(chutes_api_key, full_prompt)
                    api_response = chutes.call_chutes_model_api(full_prompt)
                else:
                    st.error("❌ Invalid model selected.")
                    return

            if api_response:
                st.session_state.analysis_response = api_response
                st.success(f"✅ Analysis complete using {selected_model}!")
            else:
                st.error(f"❌ No response received from {selected_model} model or an error occurred during the API call.")
                st.session_state.analysis_response = "Error: No response or API call failed."

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.exception(e)
            st.session_state.analysis_response = f"An application error occurred: {str(e)}"

    # Display generated prompt if available
    if st.session_state.generated_prompt:
        with st.expander("🔍 View Generated Prompt Sent to AI", expanded=False):
            st.text_area(
                "Prompt:",
                value=st.session_state.generated_prompt,
                height=300,
                disabled=True,
                key="generated_prompt_display_area"
            )
    
    # Display analysis response if available
    if st.session_state.analysis_response:
        st.markdown("---")
        st.subheader(f"📜 AI Model Analysis & Feedback ({selected_model}):")
        st.markdown(st.session_state.analysis_response) # Using markdown for better formatting of AI response
        st.markdown("---")

if __name__ == "__main__":
    run_streamlit_app()
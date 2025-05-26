# pages/1_📊_Analysis_Result.py
import streamlit as st
import datetime
import json # For the download button

# --- Helper Functions to Mimic Image Style (Copied from your previous request) ---
def display_overall_score(overall_score, max_score):
    """Displays the overall score with a progress bar."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 1.2em; font-weight: bold;">Overall Score</span>
            <span style="font-size: 2em; font-weight: bold; color: #007bff;">{overall_score}/{max_score}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    progress_percentage = int((overall_score / max_score) * 100) if max_score > 0 else 0
    st.progress(progress_percentage)
    st.caption("AI Evaluation Status: Completed")

def display_question_assessment(question_data, question_number):
    """Displays the assessment for a single question."""
    st.subheader(f"Question {question_number}: {question_data.get('question_text', 'N/A')}")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**Student Answer:** {question_data.get('student_answer_text', 'No answer provided.')}")
        if question_data.get("assessment"):
            assessment_details = question_data["assessment"]
            key_points = assessment_details.get("key_points_covered_by_student", [])
            missing_concepts = assessment_details.get("missing_concepts_in_student_answer", [])

            if key_points:
                with st.expander("Key Points Covered", expanded=False):
                    for point in key_points: st.markdown(f"- {point}")
            if missing_concepts:
                with st.expander("Missing Concepts", expanded=False):
                    for concept in missing_concepts: st.markdown(f"- {concept}")

            question_score = assessment_details.get("score", 0)
            question_max_score = assessment_details.get("max_score_possible", 10)
            relevance_percentage = int((question_score / question_max_score) * 100) if question_max_score > 0 else 0
            
            st.markdown("**Relevance to Question** (based on score)") # Clarified
            st.progress(relevance_percentage,text=f"{relevance_percentage}%")
            st.markdown("**Answer Quality** (based on score)") # Clarified
            st.progress(relevance_percentage, text=f"{relevance_percentage}%")

            if assessment_details.get("overall_question_feedback"):
                st.markdown(f"<div style='background-color: black; color:white; padding: 10px; border-radius: 5px;'>{assessment_details['overall_question_feedback']}</div>", unsafe_allow_html=True)
    with col2:
        if question_data.get("assessment"):
            score = question_data["assessment"].get("score", 0)
            max_score = question_data["assessment"].get("max_score_possible", "N/A")
            st.markdown(f"<h2 style='text-align: right; background-color: black; color: white; padding: 5px; border-radius: 5px;'>{score}/{max_score}</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: right; background-color: black; color: white; padding: 5px; border-radius: 5px;'>N/A</h2>", unsafe_allow_html=True)

    if question_data.get("assessment") and question_data["assessment"].get("rubric_component_feedback"):
        with st.expander("Detailed Rubric Feedback", expanded=False):
            for component in question_data["assessment"]["rubric_component_feedback"]:
                st.markdown(f"**{component.get('component_description', 'Component')}:**")
                if component.get("component_evaluation"): st.write(f"Evaluation: {component.get('component_evaluation')}")
                if component.get("component_strengths"): st.success(f"Strengths: {component.get('component_strengths')}")
                if component.get("component_areas_for_improvement"): st.warning(f"Areas for Improvement: {component.get('component_areas_for_improvement')}")
                st.markdown("---")
    st.markdown("---")

def display_final_feedback(overall_assessment_data):
    """Displays the final feedback summary."""
    st.header("Final Feedback Summary")
    if overall_assessment_data.get("summary_of_performance"):
        st.subheader("Summary of Performance")
        st.write(overall_assessment_data["summary_of_performance"])
    if overall_assessment_data.get("general_positive_feedback"):
        st.subheader("👍 General Positive Feedback")
        st.success(overall_assessment_data["general_positive_feedback"])
    if overall_assessment_data.get("general_areas_for_improvement"):
        st.subheader("🛠️ General Areas for Improvement")
        st.warning(overall_assessment_data["general_areas_for_improvement"])
    if overall_assessment_data.get("suggested_next_steps_or_resources"):
        st.subheader("📚 Suggested Next Steps or Resources")
        for item in overall_assessment_data["suggested_next_steps_or_resources"]: st.markdown(f"- {item}")

# --- Main Results Page Display Function ---
def show_analysis_results():
    st.set_page_config(layout="wide", page_title="AI Analysis Result")
    # The sidebar is automatically managed by Streamlit for multi-page apps.
    # You can add to it if needed: st.sidebar.header("Result Details")

    # --- Retrieve data from session state ---
    if 'analysis_results_data' not in st.session_state or not st.session_state.analysis_results_data:
        st.error("No analysis data found. Please go back to the 'AI Assignment Analyzer' page and generate an analysis first.")
        if st.button("⬅️ Back to Analyzer"):
            st.switch_page("main_analyzer_app.py") # Ensure this matches your main script's filename
        return

    assessment_data = st.session_state.analysis_results_data

    # --- Header Section ---
    st.title("📊 AI Analysis Result")
    st.caption("Review the AI-powered feedback and scoring from submitted answers.")
    st.markdown("---")

    # --- Student and Assignment Info ---
    # These should come directly from the assessment_data JSON as per your defined structure
    student_name = assessment_data.get('student_identifier', 'N/A')
    assignment_name = assessment_data.get('assignment_identifier', 'N/A')
    submission_ts_str = assessment_data.get('submission_timestamp_utc', datetime.datetime.utcnow().isoformat() + 'Z')
    
    try:
        submission_dt = datetime.datetime.fromisoformat(submission_ts_str.replace('Z', '+00:00'))
        submission_formatted = submission_dt.strftime('%B %d, %Y, %H:%M UTC')
    except ValueError:
        submission_formatted = "Invalid date format"


    st.subheader(f"Student: {student_name}")
    st.caption(f"Assignment: {assignment_name} | Submitted: {submission_formatted}")
    st.markdown("---")

    # --- Overall Score Display ---
    overall_assessment = assessment_data.get("overall_assessment")
    if overall_assessment:
        display_overall_score(
            overall_assessment.get("score", 0),
            overall_assessment.get("max_score_possible", 0)
        )
    else:
        st.warning("Overall assessment data not found in the response.")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Question by Question Breakdown ---
    question_assessments = assessment_data.get("question_assessments")
    if question_assessments:
        for i, question in enumerate(question_assessments):
            display_question_assessment(question, i + 1)
    else:
        st.info("No individual question assessments found in the response.")

    # --- Final Feedback Summary ---
    if overall_assessment:
        display_final_feedback(overall_assessment)
    st.markdown("---")

    # --- Download Button ---
    try:
        json_string_to_download = json.dumps(assessment_data, indent=2)
    except Exception as e:
        json_string_to_download = f"Error preparing JSON for download: {e}"
        st.error("Could not prepare JSON for download.")

    st.download_button(
        label="⬇️ Download Report (JSON)",
        data=json_string_to_download,
        file_name=f"{student_name.replace(' ', '_')}_assessment_report.json",
        mime="application/json",
        type="primary"
    )

    if st.button("⬅️ Analyze Another Assignment"):
        # Optionally clear specific analysis data if you want a fresh form on the main page
        # For example:
        # if 'analysis_results_data' in st.session_state:
        #     del st.session_state['analysis_results_data']
        # if 'raw_analysis_response_str' in st.session_state:
        #     del st.session_state['raw_analysis_response_str']
        # if 'generated_prompt' in st.session_state:
        #     del st.session_state['generated_prompt']
        st.switch_page("main_analyzer_app.py") # Make sure this matches your main script's filename

    # --- Footer ---
    st.markdown("---")
    current_year = datetime.datetime.now().year
    st.caption(f"© {current_year} EduAI. All rights reserved. | Terms | Privacy | Help")
    
    processing_metadata = assessment_data.get('processing_metadata', {})
    ai_confidence = assessment_data.get('ai_confidence_scores', {})
    
    model_used = processing_metadata.get('model_used', 'N/A')
    prompt_version = processing_metadata.get('prompt_version', 'N/A')
    
    overall_scoring_conf = ai_confidence.get('overall_scoring_confidence', 'N/A')
    feedback_gen_conf = ai_confidence.get('feedback_generation_confidence', 'N/A')

    overall_scoring_conf_display = f"{overall_scoring_conf*100:.0f}%" if isinstance(overall_scoring_conf, (int, float)) else 'N/A'
    feedback_gen_conf_display = f"{feedback_gen_conf*100:.0f}%" if isinstance(feedback_gen_conf, (int, float)) else 'N/A'

    st.caption(f"Processing Info: Model - {model_used}, Prompt Ver - {prompt_version}")
    st.caption(f"AI Scoring Confidence: {overall_scoring_conf_display} | AI Feedback Confidence: {feedback_gen_conf_display}")

# This ensures the page renders when Streamlit navigates to it.
if __name__ == "__main__": # Technically not needed for pages, but good practice
    show_analysis_results()

# Call the main function to render the page.
# For Streamlit pages, the script is run from top to bottom when navigated to.
show_analysis_results()

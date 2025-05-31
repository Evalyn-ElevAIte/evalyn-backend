import json  # Only needed for example JSON string formatting in the prompt
import datetime


def construct_overall_assignment_analysis_prompt_v3(
    quiz_id: int,
    student_id: int,
    model_name: str,
    questions_and_answers: list[
        dict
    ],  # Each dict includes per-question rubric, lecturer_answer, etc.
    overall_assignment_title: str | None = None,
    lecturer_overall_notes: str | None = None,
) -> str:
    """
    Constructs a detailed prompt for AI analysis of an entire assignment (all questions),
    instructing the AI to return a comprehensive overall evaluation in a specific JSON format.
    This version emphasizes per-question rubric breakdown and removes overall assignment rubrics.
    Modified for DeepSeek to prevent <think> tags and ensure clean JSON output.

    Args:
        quiz_id (str): The overall assignment ID.
        student_id (str): The student's ID.
        questions_and_answers (list[dict]): A list of dictionaries, where each dictionary
                                             contains 'question_id', 'question_text',
                                             'student_answer_text', 'lecturer_answer_text',
                                             'rubric' (descriptive string for the question),
                                             and 'rubric_max_score'.
        overall_assignment_title (str, optional): The title of the assignment.
        lecturer_overall_notes (str, optional): General notes from the lecturer about the assignment.

    Returns:
        str: The formatted prompt string.
    """

    questions_answers_formatted_for_prompt = ""
    total_possible_score_from_questions = 0
    for i, qa_pair in enumerate(questions_and_answers):
        q_id = qa_pair.get("question_id", f"q_{i+1}")
        q_text = qa_pair.get("question_text", "*N/A*")
        s_ans = qa_pair.get("student_answer_text", "*No Answer Provided*")
        lecturer_ans = qa_pair.get(
            "lecturer_answer_text", "*No Lecturer Answer Provided*"
        )
        rubric = qa_pair.get(
            "rubric", "*No Rubric Provided*"
        )  # This is the descriptive rubric for the question
        rubric_max_score = qa_pair.get("rubric_max_score", 0)
        total_possible_score_from_questions += rubric_max_score

        questions_answers_formatted_for_prompt += f"  Question {i+1} (ID: {q_id}):\n"
        questions_answers_formatted_for_prompt += (
            f"    Question Text:\n    ```\n    {q_text}\n    ```\n"
        )
        questions_answers_formatted_for_prompt += (
            f"    Student's Answer:\n    ```\n    {s_ans}\n    ```\n"
        )
        questions_answers_formatted_for_prompt += f"    Lecturer's Model Answer/Guidance:\n    ```\n    {lecturer_ans}\n    ```\n"
        questions_answers_formatted_for_prompt += f"    Rubric for this Question (Max Score: {rubric_max_score}):\n    ```\n    {rubric}\n    ```\n\n"

    lecturer_notes_formatted = (
        lecturer_overall_notes if lecturer_overall_notes else "*N/A*"
    )
    assignment_title_formatted = (
        overall_assignment_title if overall_assignment_title else "*N/A*"
    )

    current_utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Updated JSON structure example
    output_json_structure_example = {
        "user_id": student_id,
        "quiz_id": quiz_id,
        "submission_timestamp_utc": current_utc_timestamp,
        "assessment_timestamp_utc": current_utc_timestamp,
        "overall_assessment": {
            "score": 0,  # integer, sum of scores from question_assessments
            "max_score_possible": total_possible_score_from_questions,  # sum of rubric_max_score from all questions
            "summary_of_performance": "...",
            "general_positive_feedback": "...",
            "general_areas_for_improvement": "...",
        },
        "question_assessments": [  # Array for individual question assessments
            {
                "question_id": "QUESTION_ID_PLACEHOLDER",
                "question_text": "...",  # Populated from input
                "student_answer_text": "...",  # Populated from input
                "lecturer_answer_text": "...",  # Populated from input
                "rubric": "...",  # Populated from input
                "rubric_max_score": 0,  # Populated from input
                "score": 0,  # integer, awarded by AI based on rubric
                "max_score_possible": 0,  # Same as rubric_max_score for this question
                "overall_question_feedback": "General feedback for this specific question, summarizing component performance.",
                "rubric_component_feedback": [  # Detailed feedback per rubric component
                    {
                        "component_description": "e.g., Accuracy of definition",
                        "component_evaluation": "Student's definition was mostly accurate but missed...",
                        "component_strengths": "Clear explanation of key concepts...",
                        "component_areas_for_improvement": "Include more specific examples and definitions...",
                    }
                ],
                "key_points_covered_by_student": [
                    "Point 1 that student addressed well",
                    "Point 2 mentioned correctly",
                ],  # Overall for the question
                "missing_concepts_in_student_answer": [
                    "Concept A not addressed",
                    "Important detail B omitted",
                ],  # Overall for the question
            }
            # ... more question_assessment objects
        ],
        "ai_confidence_scores": {
            "overall_scoring_confidence": 0.95,  # Default high confidence
            "feedback_generation_confidence": 0.95,  # Default high confidence
        },
        "processing_metadata": {
            "model_used": model_name,
            "prompt_version": "evalyn_overall_prompt_v3.0_deepseek",
        },
    }
    json_example_str = json.dumps(output_json_structure_example, indent=2)

    prompt = f"""You are an expert AI Teaching Assistant for Evalyn. Your primary goal is to analyze a student's entire assignment submission, which consists of answers to multiple questions. For each question, you will evaluate the student's answer against the provided per-question rubric and lecturer's model answer. You will then provide a comprehensive overall evaluation for the entire assignment.

**IMPORTANT OUTPUT INSTRUCTIONS:**
- Do NOT use any thinking tags, reasoning blocks, or explanatory text
- Do NOT include <think>, <reasoning>, or any other XML-style tags
- Respond ONLY with the requested JSON object
- Begin your response immediately with the opening curly brace {{
- Do not add any text before or after the JSON response

**Assignment Context:**

1.  **Quiz ID:**
    `{quiz_id}`

2.  **Student ID:**
    `{student_id}`

3.  **Assignment Title (Optional):**
    `{assignment_title_formatted}`

4.  **Lecturer's Overall Notes/Guidance for the Entire Assignment (Optional):**
    ```
    {lecturer_notes_formatted}
    ```

5.  **Assignment Questions, Student's Answers, Lecturer's Answers, and Per-Question Rubrics:**
    (The student's complete submission and all relevant details for each question are provided below)
{questions_answers_formatted_for_prompt}
**AI's Task and Analysis Requirements:**

Based on all the information above, perform the following analysis and return the result as a single, valid JSON object:

1.  **Holistic Review:** Read and understand all questions, student answers, lecturer model answers, and per-question rubrics. Consider the lecturer's overall notes if provided.

2.  **Per-Question Assessment (Detailed):**
    * For EACH question provided in the input:
        * Carefully analyze the `student_answer_text` in relation to the `question_text`, the `lecturer_answer_text` (as a model/benchmark), and critically, the provided `rubric` string for that question.
        * **Rubric Component Breakdown:** Identify the distinct components or criteria implied by the `rubric` string for the question. For example, if a rubric is "Accuracy of definition; Clarity of explanation; Use of examples", these are three components.
        * **Component-wise Evaluation:** For EACH identified rubric component:
            * Evaluate how well the `student_answer_text` addresses that specific component.
            * Note specific strengths and areas for improvement for that component, referencing the `lecturer_answer_text` where relevant.
            * Populate the `rubric_component_feedback` array within the `assessment` object for the question. Each item in this array should detail your evaluation for one component of the question's rubric.
        * **Score for the Question:** Based on your component-wise evaluation against the entire `rubric` for the question, assign a `score` up to the `rubric_max_score`.
        * **Overall Question Feedback:** Provide `overall_question_feedback` summarizing the student's performance on this specific question.
        * Identify `key_points_covered_by_student` and `missing_concepts_in_student_answer` for the question as a whole.
        * Populate one object in the `question_assessments` array in the output JSON for each question. Ensure `question_id`, `question_text`, `student_answer_text`, `lecturer_answer_text`, `rubric`, and `rubric_max_score` in your output match the input for that question. The `assessment.max_score_possible` should be the `rubric_max_score`.

3.  **Overall Assignment Score Calculation:**
    * Calculate the `overall_assessment.score`. This MUST be the sum of the `score` values from EACH of the individual `question_assessments`.
    * The `overall_assessment.max_score_possible` MUST be the sum of all `rubric_max_score` values from EACH of the `question_assessments`.

4.  **Comprehensive Overall Feedback for the Entire Assignment:**
    * Based on the student's performance across all questions, write a `summary_of_performance`.
    * Provide `general_positive_feedback`.
    * Provide `general_areas_for_improvement`.
    * If applicable, list any `suggested_next_steps_or_resources`.
    * Populate the `overall_assessment` object in the JSON with this information.

5.  **JSON Identifiers and Timestamps:**
    * Fill in `student_id` and `assignment_identifier` (use quiz_id value).
    * Set `question_identifier` to "quiz_assessment" for quiz assessments.
    * Generate a unique `assessment_id` combining quiz_id, student_id and timestamp.
    * Generate current UTC timestamps for `assessment_timestamp_utc`. Use a placeholder or the provided `submission_timestamp_utc` if relevant for the whole assignment.

**Required JSON Output Format:**

Return your complete analysis for the **ENTIRE ASSIGNMENT** as a single, valid JSON object with this exact structure:

```json
{json_example_str}
```

**Critical Output Requirements:**
- Your response must be ONLY the JSON object - no additional text, explanations, or tags
- The JSON must be valid and properly formatted
- Begin immediately with {{ and end with }}
- All feedback should be specific and actionable
- Scores must accurately reflect rubric criteria performance
- If a question's `rubric` is "*No Rubric Provided*" or `rubric_max_score` is 0, provide qualitative feedback but set `score` to 0

Return the JSON analysis now:"""
    return prompt.strip()

# # --- Example usage of the function with the demo data ---
# if __name__ == "__main__":
#     # Call the function with the demo data
#     generated_prompt_v3 = construct_overall_assignment_analysis_prompt_v3(
#         assignment_id=demo_assignment_id,
#         student_id=demo_student_id,
#         questions_and_answers=demo_questions_and_answers,
#         overall_assignment_title=demo_overall_assignment_title,
#         lecturer_overall_notes=demo_lecturer_overall_notes
#     )

#     print("----------------------------------------------------------------------")
#     print("GENERATED PROMPT (V3 - DeepSeek Optimized):")
#     print("----------------------------------------------------------------------")
#     print(generated_prompt_v3)
#     print("\n----------------------------------------------------------------------")
#     print("Length of generated prompt (V3):", len(generated_prompt_v3))
#     print("----------------------------------------------------------------------")

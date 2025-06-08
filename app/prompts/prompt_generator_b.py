import json
import datetime


def construct_model_answer_comparison_prompt_b(
    quiz_id: int,
    student_id: int,
    model_name: str,
    questions_and_answers: list[
        dict
    ],  # Each dict now only needs lecturer_answer, not rubric.
    overall_assignment_title: str | None = None,
    lecturer_overall_notes: str | None = None,
) -> str:
    """
    Constructs a detailed prompt for AI analysis of an entire assignment (Prompt B).

    This version instructs the AI to evaluate based on a direct comparison to the
    lecturer's model answer, EXCLUDING any rubric. It still requires the
    same comprehensive JSON output as the original prompt, but removes all
    rubric-related fields like 'rubric_component_feedback'.

    Args:
        quiz_id (int): The overall assignment ID.
        student_id (int): The student's ID.
        model_name (str): The name of the AI model being used.
        questions_and_answers (list[dict]): A list of dictionaries, where each contains
                                             'question_id', 'question_text',
                                             'student_answer_text', 'lecturer_answer_text',
                                             and 'max_score'.
        overall_assignment_title (str, optional): The title of the assignment.
        lecturer_overall_notes (str, optional): General notes from the lecturer.

    Returns:
        str: The formatted prompt string for the control experiment (Prompt B).
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
        # We now use 'max_score' instead of 'rubric_max_score' for clarity
        max_score = qa_pair.get("max_score", 0)
        total_possible_score_from_questions += max_score

        questions_answers_formatted_for_prompt += f"  Question {i+1} (ID: {q_id}, Max Score: {max_score}):\n"
        questions_answers_formatted_for_prompt += (
            f"    Question Text:\n    ```\n    {q_text}\n    ```\n"
        )
        questions_answers_formatted_for_prompt += (
            f"    Student's Answer:\n    ```\n    {s_ans}\n    ```\n"
        )
        questions_answers_formatted_for_prompt += f"    Lecturer's Model Answer/Guidance:\n    ```\n    {lecturer_ans}\n    ```\n\n"

    lecturer_notes_formatted = (
        lecturer_overall_notes if lecturer_overall_notes else "*N/A*"
    )
    assignment_title_formatted = (
        overall_assignment_title if overall_assignment_title else "*N/A*"
    )

    current_utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # MODIFIED JSON structure example: 'rubric' and 'rubric_component_feedback' are removed.
    output_json_structure_example = {
        "user_id": student_id,
        "quiz_id": quiz_id,
        "submission_timestamp_utc": current_utc_timestamp,
        "assessment_timestamp_utc": current_utc_timestamp,
        "overall_assessment": {
            "score": 0,
            "max_score_possible": total_possible_score_from_questions,
            "summary_of_performance": "...",
            "general_positive_feedback": "...",
            "general_areas_for_improvement": "...",
        },
        "question_assessments": [
            {
                "question_id": 0,
                "question_text": "...",
                "student_answer_text": "...",
                "lecturer_answer_text": "...",
                "max_score_possible": 0, # Populated from input 'max_score'
                "score": 0, # Awarded by AI based on comparison to model answer
                "overall_question_feedback": "General feedback for this specific question.",
                "key_points_covered_by_student": [
                    "Point 1 that student addressed well by comparing to model answer."
                ],
                "missing_concepts_in_student_answer": [
                    "Concept A from the model answer that was not addressed."
                ],
            }
            # ... more question_assessment objects
        ],
        "ai_confidence_scores": {
            "overall_scoring_confidence": 0.95,
            "feedback_generation_confidence": 0.95,
        },
        "processing_metadata": {
            "model_used": model_name,
            "prompt_version": "evalyn_model_answer_comparison_prompt_b_1.0",
        },
    }
    json_example_str = json.dumps(output_json_structure_example, indent=2)

    prompt = f"""You are an expert AI Teaching Assistant for Evalyn. Your primary goal is to analyze a student's entire assignment submission. For each question, you will evaluate the student's answer by **comparing it directly against the provided lecturer's model answer**. You will then provide a comprehensive overall evaluation for the entire assignment in the specified JSON format.

**IMPORTANT OUTPUT INSTRUCTIONS:**
- Do NOT use any thinking tags, reasoning blocks, or explanatory text.
- Respond ONLY with the requested JSON object.
- Begin your response immediately with the opening curly brace {{ and end with }}.

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

5.  **Assignment Questions, Student's Answers, and Lecturer's Answers:**
    (The student's complete submission and all relevant details for each question are provided below)
{questions_answers_formatted_for_prompt}
**AI's Task and Analysis Requirements:**

Based on all the information above, perform the following analysis and return the result as a single, valid JSON object:

1.  **Holistic Review:** Read and understand all questions, student answers, and lecturer model answers. Consider the lecturer's overall notes if provided.

2.  **Per-Question Assessment (Detailed):**
    * For EACH question provided in the input:
        * **Crucial Instruction:** Your evaluation for each question MUST be based on a direct comparison between the `student_answer_text` and the `lecturer_answer_text`. The lecturer's answer is the benchmark for a perfect response.
        * **Score for the Question:** Based on how well the student's answer captures the key concepts, accuracy, and depth of the model answer, assign a `score` up to the `max_score` specified for that question.
        * **Overall Question Feedback:** Provide `overall_question_feedback` summarizing the student's performance on this specific question based on the comparison.
        * Identify `key_points_covered_by_student` (points where the student's answer matched the model answer) and `missing_concepts_in_student_answer` (important points from the model answer that the student omitted).
        * Populate one object in the `question_assessments` array in the output JSON for each question. Ensure all fields match the provided example and the data from the prompt input.

3.  **Overall Assignment Score Calculation:**
    * Calculate the `overall_assessment.score`. This MUST be the sum of the `score` values from EACH of the individual `question_assessments`.
    * The `overall_assessment.max_score_possible` MUST be the sum of all `max_score` values from EACH of the `question_assessments`.

4.  **Comprehensive Overall Feedback for the Entire Assignment:**
    * Based on the student's performance across all questions, write a `summary_of_performance`, `general_positive_feedback`, and `general_areas_for_improvement`.
    * Populate the `overall_assessment` object in the JSON with this information.

**Required JSON Output Format:**

Return your complete analysis for the ENTIRE ASSIGNMENT as a single, valid JSON object with this exact structure. Note that rubric-related fields have been removed.

```json
{json_example_str}
"""
    return prompt.strip()

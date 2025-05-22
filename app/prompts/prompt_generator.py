import json # Only needed for example JSON string formatting in the prompt

"""
Sample JSON structure for the questions and answers
sample_q_and_a = [
        {
            "question_id": "ECON202_Q1",
            "question_text": "Define 'opportunity cost' and provide an example.",
            "student_answer_text": "Opportunity cost is what you give up to get something else. Like if I buy a book, the opportunity cost is the movie I couldn't watch."
        },
        {
            "question_id": "ECON202_Q2",
            "question_text": "Explain the law of demand with a diagram.",
            "student_answer_text": "The law of demand means when price goes up, people buy less. If price goes down, people buy more. (No diagram provided in this text example)"
        },
        {
            "question_id": "ECON202_Q3",
            "question_text": "What are two primary functions of money?",
            "student_answer_text": "Money is a medium of exchange and a store of value. You use it to buy stuff and you can save it."
        }
    ]
"""

def construct_overall_assignment_analysis_prompt(
    assignment_id: str,
    student_id: str,
    questions_and_answers: list[dict], # List of dicts, each with 'question_id', 'question_text', 'student_answer_text'
    overall_assignment_rubrics: list[dict], # Rubrics for the entire assignment
    overall_assignment_title: str | None = None, # Optional
    lecturer_overall_notes: str | None = None # Optional: General notes from lecturer about what to look for
) -> str:
    """
    Constructs a detailed prompt for AI analysis of an entire assignment (all questions),
    instructing the AI to return a comprehensive overall evaluation in a specific JSON format.

    Args:
        assignment_id (str): The overall assignment ID.
        student_id (str): The student's ID.
        questions_and_answers (list[dict]): A list of dictionaries, where each dictionary
                                            contains 'question_id', 'question_text',
                                            and 'student_answer_text'.
        overall_assignment_rubrics (list[dict]): A list of dictionaries, where each dictionary
                                                 defines an overall rubric criterion for the entire assignment.
                                                 Example: [{"criterion_id": "overall_01", "criterion_name": "Clarity",
                                                           "max_score": 10, "description": "Overall clarity..."}]
        overall_assignment_title (str, optional): The title of the assignment.
        lecturer_overall_notes (str, optional): General notes from the lecturer about the assignment.

    Returns:
        str: The formatted prompt string.
    """

    questions_answers_formatted_for_prompt = ""
    for i, qa_pair in enumerate(questions_and_answers):
        q_id = qa_pair.get('question_id', f"q_{i+1}")
        q_text = qa_pair.get('question_text', '*N/A*')
        s_ans = qa_pair.get('student_answer_text', '*No Answer Provided*')
        questions_answers_formatted_for_prompt += f"  Question {i+1} (ID: {q_id}):\n"
        questions_answers_formatted_for_prompt += f"    ```\n    {q_text}\n    ```\n"
        questions_answers_formatted_for_prompt += f"  Student's Answer to Question {i+1}:\n"
        questions_answers_formatted_for_prompt += f"    ```\n    {s_ans}\n    ```\n\n"

    overall_rubrics_formatted_for_prompt = "\n".join(
        [
            f"    - Criterion ID: {r['criterion_id']}, Name: {r['criterion_name']}, Max Score: {r['max_score']}, Description: {r['description']}"
            for r in overall_assignment_rubrics
        ]
    )
    total_max_score_overall = sum(r['max_score'] for r in overall_assignment_rubrics)

    lecturer_notes_formatted = lecturer_overall_notes if lecturer_overall_notes else "*N/A*"
    assignment_title_formatted = overall_assignment_title if overall_assignment_title else "*N/A*"


    # This is the comprehensive JSON structure the AI is expected to return for the entire assignment.
    # This matches the structure in evalyn_ai_json_output_v1
    output_json_structure_example = {
      "assessment_id": "unique_assessment_run_id",
      "student_identifier": student_id,
      "assignment_identifier": assignment_id,
      "question_identifier": "overall_assignment", # Indicates this is for the whole assignment
      "submission_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ", # AI can generate or use a placeholder
      "assessment_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ", # AI generates current time
      "overall_assessment": {
        "score": 0, # integer, sum of overall_assignment_rubrics scores
        "max_score_possible": total_max_score_overall,
        "summary_of_performance": "...",
        "general_positive_feedback": "...",
        "general_areas_for_improvement": "...",
        "suggested_next_steps_or_resources": ["...", "..."]
      },
      "rubric_based_assessment": [ # This array will contain objects for EACH of the overall_assignment_rubrics
        {
          "criterion_id": "OVERALL_RUBRIC_CRITERION_ID_PLACEHOLDER",
          "criterion_name": "OVERALL_RUBRIC_CRITERION_NAME_PLACEHOLDER",
          "score": 0, # integer
          "max_score": 0, # integer
          "observations": "...",
          "strengths_for_criterion": "...",
          "areas_for_improvement_for_criterion": "...",
          "specific_feedback_for_criterion": "..."
        }
        # ... more overall rubric criteria objects
      ],
      "identified_specific_mistakes": [ # Optional: Mistakes identified across any of the answers
        {
          "mistake_description": "...",
          "context_or_quote_from_answer": "From Question X: ...", # Optional
          "suggested_correction": "..."
        }
      ],
      "ai_confidence_scores": { # Optional
        "overall_scoring_confidence": 0.0, # float between 0 and 1
        "feedback_generation_confidence": 0.0
      },
      "processing_metadata": { # Optional
        "model_used": "gemini-1.5-pro-latest", # Example
        "prompt_version": "evalyn_overall_prompt_vX.Y"
      }
    }
    json_example_str = json.dumps(output_json_structure_example, indent=2)

    prompt = f"""You are an expert AI Teaching Assistant for Evalyn. Your primary goal is to analyze a student's entire assignment submission, which consists of answers to multiple questions. You will then provide a comprehensive overall evaluation based on the provided materials and overall assignment rubrics.

**Assignment Context:**

1.  **Overall Assignment ID:**
    `{assignment_id}`

2.  **Student ID:**
    `{student_id}`

3.  **Assignment Title (Optional):**
    `{assignment_title_formatted}`

4.  **Lecturer's Overall Notes/Guidance (Optional):**
    ```
    {lecturer_notes_formatted}
    ```

5.  **Assignment Questions and Student's Submitted Answers:**
    (The student's complete submission to all questions is provided below)
{questions_answers_formatted_for_prompt}
**Overall Assignment Grading Rubrics:**
------------------------------------
The total maximum score possible for this entire assignment is {total_max_score_overall}.
Evaluate the student's entire submission (all answers considered collectively) against these overall rubrics:
{overall_rubrics_formatted_for_prompt}
------------------------------------

**AI's Task and Output Instructions for the ENTIRE ASSIGNMENT:**

Based on all the information above (all questions, all answers, and the overall assignment rubrics), please perform the following and structure your entire response as a single, valid JSON object:

1.  **Holistic Review:** Read and understand all the questions and the student's corresponding answers. Consider the lecturer's overall notes if provided.
2.  **Overall Rubric Evaluation:**
    * For EACH "Overall Assignment Rubric" criterion provided, evaluate the student's entire body of work (all answers combined) and assign a score up to the 'Max Score' for that overall criterion.
    * Provide specific observations, strengths (citing examples from student's answers if possible), areas for improvement, and actionable feedback for EACH overall rubric criterion.
    * Populate the `rubric_based_assessment` array in the JSON with these evaluations. Each object in this array corresponds to one of the *overall assignment rubrics*.
3.  **Overall Score Calculation:**
    * Calculate an `overall_score` for the entire assignment. This should be the sum of the scores you assign for each of the `overall_assignment_rubrics`.
    * The `max_score_possible` in the `overall_assessment` object should be {total_max_score_overall}.
4.  **Comprehensive Overall Feedback:**
    * Write a `summary_of_performance` that gives a general overview of the student's work across the entire assignment.
    * Provide `general_positive_feedback` highlighting what the student did well across all answers.
    * Provide `general_areas_for_improvement` pointing out broader areas the student should focus on based on their complete submission.
    * If applicable, list any `suggested_next_steps_or_resources`.
    * Populate the `overall_assessment` object in the JSON with this information.
5.  **Specific Mistakes (Optional):**
    * If you identify any notable `identified_specific_mistakes` (e.g., recurring factual errors, significant miscalculations) across any of the student's answers that weren't fully captured by the overall rubric feedback, list them. Indicate which question the mistake pertains to if possible. This is optional.
6.  **JSON Identifiers:**
    * Fill in the `student_identifier` and `assignment_identifier` in the JSON with the provided values.
    * Use a value like "overall_assignment" or the actual `assignment_id` for the `question_identifier` field in the root of the JSON to signify this is an overall evaluation.
    * Generate current UTC timestamps for `assessment_timestamp_utc`. Use a placeholder or omit `submission_timestamp_utc` if not readily available for the whole assignment.

**Output JSON Format (Strict Adherence Required):**

Return your complete analysis for the **ENTIRE ASSIGNMENT** as a single, valid JSON object. The structure must be as follows:

```json
{json_example_str}
```

**Important:**
* Ensure all placeholder values in the example JSON structure are appropriately filled based on your evaluation and the input data. For example, the `assignment_id` and `student_id` fields in your output JSON should match the input.
* The `rubric_based_assessment` array in your output JSON must correspond to the `overall_assignment_rubrics` provided in this prompt.

Begin your JSON output for the entire assignment now:
"""
    return prompt.strip()
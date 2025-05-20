import json # Only needed for the example in main, not for the function itself

def construct_assignment_analysis_prompt(assignment_question, evaluation_metrics, contextual_requirements, lecturer_answer, student_answer):
    """
    Constructs a detailed prompt for assignment analysis.

    Args:
        assignment_question (str): The full assignment question.
        evaluation_metrics (list): A list of strings, where each string is an evaluation metric.
        contextual_requirements (list): A list of strings, where each string is a contextual requirement.
        lecturer_answer (str): The lecturer's ideal answer or key points.
        student_answer (str): The student's submitted answer.

    Returns:
        str: The formatted prompt string.
    """
    
    # Format metrics and requirements into bulleted lists
    metrics_formatted = "\n".join([f"* Metric {i+1}: {metric}" for i, metric in enumerate(evaluation_metrics)])
    requirements_formatted = "\n".join([f"* Requirement {i+1}: {req}" for i, req in enumerate(contextual_requirements)])

    prompt = f"""
You are an AI Teaching Assistant. Your primary goal is to analyze a student's assignment submission based on the provided materials and offer constructive feedback.

**Assignment Context:**

1.  **Assignment Question:**
    ```
    {assignment_question}
    ```

2.  **Evaluation Metrics (from Lecturer):**
{metrics_formatted}

3.  **Specific Contextual Requirements/Constraints:**
{requirements_formatted}

4.  **Lecturer's Ideal Answer / Key Points:**
    ```
    {lecturer_answer}
    ```

5.  **Student's Submitted Answer:**
    ```
    {student_answer}
    ```

**AI's Task and Output Instructions:**

Based on all the information above, please perform the following:

A.  **Correctness Evaluation:**
    * Is the student's answer fundamentally correct, partially correct, or incorrect when compared against the lecturer's ideal answer and the assignment question?
    * Briefly explain your reasoning.

B.  **Comparative Analysis with Lecturer's Answer:**
    * Identify key similarities between the student's answer and the lecturer's ideal answer.
    * Highlight significant differences, missing information, or misunderstandings in the student's answer.

C.  **Evaluation Against Metrics and Constraints:**
    * For each "Evaluation Metric" listed above, assess how well the student's answer meets it. Be specific.
    * For each "Specific Contextual Requirement/Constraint," state whether the student has met it.

D.  **Constructive Feedback and Suggestions for Improvement:**
    * Provide clear, actionable feedback to the student.
    * Focus on 2-3 key areas where the student can improve their understanding or their answer.
    * Suggestions should be specific (e.g., "Consider elaborating on [specific point X] by providing an example, similar to how the lecturer's answer explains [related point Y].")
    * Maintain a supportive and encouraging tone.

**Output Format:**
Please structure your response clearly, using headings for each section (A, B, C, D).
"""
    return prompt.strip() # Use strip() to remove leading/trailing whitespace from the f-string
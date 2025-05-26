from fastapi import APIRouter, HTTPException
from typing import Optional
from app.prompts.prompt_generator import construct_overall_assignment_analysis_prompt_v3
from app.core.llm.llm_factory import get_llm_api_call_function
from app.models.models import Quiz, Question

router = APIRouter()

@router.post("/analyze-quiz")
async def analyze_quiz(
    quiz_id: str,
    model_name: str = "azure",
    overall_assignment_title: Optional[str] = None,
    lecturer_overall_notes: Optional[str] = None
):
    """
    Analyze a quiz by:
    1. Getting quiz data from database
    2. Generating analysis prompt
    3. Sending to selected LLM model
    4. Returning analysis results
    
    Args:
        quiz_id: ID of quiz to analyze
        model_name: LLM model to use (deepseek-chat, gemini, azure-openai)
        overall_assignment_title: Optional assignment title
        lecturer_overall_notes: Optional overall notes from lecturer
    """
    try:
        # Get quiz and questions from database
        quiz = await Quiz.get(id=quiz_id).prefetch_related("questions")
        questions = await quiz.questions.all()
        
        # Prepare questions_and_answers structure for prompt generator
        questions_and_answers = []
        for question in questions:
            questions_and_answers.append({
                "question_id": question.question_id,
                "question_text": question.text,
                "student_answer_text": question.student_answer_text,
                "lecturer_answer_text": question.lecturer_answer_text,
                "rubric": question.rubric,
                "rubric_max_score": question.rubric_max_score
            })
        
        # Generate analysis prompt
        prompt = construct_overall_assignment_analysis_prompt_v3(
            assignment_id=quiz.assignment_id,
            student_id=quiz.student_id,
            questions_and_answers=questions_and_answers,
            overall_assignment_title=overall_assignment_title,
            lecturer_overall_notes=lecturer_overall_notes
        )
        
        # Get LLM instance and analyze
        llm = get_llm_api_call_function(model_name)
        analysis_result = await llm.analyze(prompt)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "model_used": model_name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quiz analysis failed: {str(e)}"
        )
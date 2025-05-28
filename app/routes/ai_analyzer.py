from fastapi import APIRouter, HTTPException
from typing import Optional
from app.prompts.prompt_generator import construct_overall_assignment_analysis_prompt_v3
from app.core.llm.llm_factory import get_llm_api_call_function
from app.models.models import Quiz, Question
from fastapi import Depends
from app.dependencies import get_current_user
from app.models.models import QuizParticipant, QuestionResponse
from app.schemas.question_response import (
    QuestionResponseCreate,
    QuestionResponseRead,
    BulkQuestionResponseCreate,
    QuestionResponseToAI,
    BulkQuestionResponseToAI
)

router = APIRouter()

@router.post("/analyze-quiz")
async def analyze_quiz(
    quiz_id: int,
    model_name: str = "azure",
    current_user=Depends(get_current_user)
):
    """
    Generate input data and analyze quiz answers for the specified student and quiz
    
    Args:
        quiz_id: ID of the quiz to analyze
        model_name: LLM model to use (deepseek-chat, gemini, azure-openai)
        current_user: Current authenticated user
    """
    try:
        # Check if quiz exists and get its attributes
        quiz = await Quiz.get_or_none(id=quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Check if student is participant in the quiz
        participant = await QuizParticipant.get_or_none(
            user_id=current_user.id,
            quiz_id=quiz_id
        )
        if not participant:
            raise HTTPException(
                status_code=403,
                detail="Student is not a participant in this quiz"
            )

        # Get all questions and student responses for this quiz
        responses = await QuestionResponse.filter(
            user_id=current_user.id,
            question__quiz_id=quiz_id
        ).prefetch_related('question')
        
        # Get all questions for the quiz to ensure we include unanswered ones
        questions = await Question.filter(quiz_id=quiz_id)
        
        # Transform responses for AI analysis
        ai_responses = []
        for question in questions:
            # Find matching response for this question
            response = next((r for r in responses if r.question_id == question.id), None)
            
            ai_responses.append(QuestionResponseToAI(
                question_id=question.id,
                answer={'text': response.answer} if response else {'text': ''},
                question_text=question.text,
                question_type=question.type,
                lecturer_answer_text=question.expected_answer,
                rubric=question.rubric,
                rubric_max_score=question.rubric_max_score
            ))
        
        if not ai_responses:
            raise HTTPException(
                status_code=404,
                detail="No answers found for analysis"
            )
        
        # Prepare questions_and_answers structure for prompt generator
        questions_and_answers = []
        for response in ai_responses:
            questions_and_answers.append({
                "question_id": response.question_id,
                "question_text": response.question_text,
                "student_answer_text": response.answer.get('text', ''),
                "lecturer_answer_text": response.lecturer_answer_text,
                "rubric": response.rubric,
                "rubric_max_score": response.rubric_max_score
            })
        
        # Generate analysis prompt
        prompt = construct_overall_assignment_analysis_prompt_v3(
            assignment_id=str(quiz.id),
            student_id=str(current_user.id),
            model_name=model_name,
            questions_and_answers=questions_and_answers,
            overall_assignment_title=quiz.title,
            lecturer_overall_notes=quiz.lecturer_overall_notes
        )
        
        # Get LLM instance and analyze
        # llm = get_llm_api_call_function(model_name)
        analysis_result =  get_llm_api_call_function(prompt,model_name)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "model_used": model_name,
            "quiz_id": quiz.id,
            "student_id": current_user.id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quiz analysis failed: {str(e)}"
        )
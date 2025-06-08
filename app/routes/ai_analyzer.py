from fastapi import APIRouter, HTTPException
from typing import Optional
from app.prompts.prompt_generator import construct_overall_assignment_analysis_prompt_v3
from app.prompts.prompt_generator_b import construct_model_answer_comparison_prompt_b
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
    BulkQuestionResponseToAI,
)
from app.services.assesment_service import AssessmentService

router = APIRouter()


@router.post("/analyze-quiz/{quiz_id}")
async def analyze_quiz(
    quiz_id: int,
    model_name: str = "azure",
    current_user=Depends(get_current_user),
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
            user_id=current_user.id, quiz_id=quiz_id
        )
        if not participant:
            raise HTTPException(
                status_code=403, detail="Student is not a participant in this quiz"
            )

        # Get all questions and student responses for this quiz from table (temporary)
        responses = await QuestionResponse.filter(
            user_id=current_user.id, question__quiz_id=quiz_id
        ).prefetch_related("question")

        # Get all questions for the quiz to ensure we include unanswered ones
        questions = await Question.filter(quiz_id=quiz_id)

        # Transform responses for AI analysis
        ai_responses = []
        for question in questions:
            # Find matching response for this question
            response = next(
                (r for r in responses if r.question_id == question.id), None
            )

            ai_responses.append(
                QuestionResponseToAI(
                    question_id=question.id,
                    answer={"text": response.answer} if response else {"text": ""},
                    question_text=question.text,
                    question_type=question.type,
                    lecturer_answer_text=question.expected_answer,
                    rubric=question.rubric,
                    rubric_max_score=question.rubric_max_score,
                )
            )

        if not ai_responses:
            raise HTTPException(status_code=404, detail="No answers found for analysis")

        # Prepare questions_and_answers structure for prompt generator
        questions_and_answers = []
        for response in ai_responses:
            questions_and_answers.append(
                {
                    "question_id": response.question_id,
                    "question_text": response.question_text,
                    "student_answer_text": response.answer.get("text", ""),
                    "lecturer_answer_text": response.lecturer_answer_text,
                    "rubric": response.rubric,
                    "rubric_max_score": response.rubric_max_score,
                }
            )

        # Generate analysis prompt
        prompt = construct_overall_assignment_analysis_prompt_v3(
            quiz_id=quiz.id,  # Pass as int
            student_id=current_user.id,  # Pass as int
            model_name=model_name,
            questions_and_answers=questions_and_answers,
            overall_assignment_title=quiz.title,
            lecturer_overall_notes=quiz.lecturer_overall_notes,
        )

        # Get LLM API call function
        llm_call_function = get_llm_api_call_function(model_name)
        
        # Analyze with LLM
        analysis_result, input_tokens = llm_call_function(prompt)

        print(f"Analysis Result: {analysis_result}")
        print(f"Input Tokens: {input_tokens}")

        # Create assessment from analysis result
        assessment = await AssessmentService.create_assessment_from_json(
            analysis_result
        )
        if not assessment:
            raise HTTPException(
                status_code=500, detail="Failed to create assessment from analysis"
            )

        # Update participant status to graded
        # participant.status = "graded"
        # await participant.save()

        return {
            "success": True,
            "analysis": analysis_result,
            "assessment_id": assessment.id,  # Return the integer ID
            "model_used": model_name,
            "quiz_id": quiz.id,
            "student_id": current_user.id,
            "input_tokens": input_tokens, # Add input tokens to the response
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions with their original status code
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz analysis failed: {str(e)}")


@router.post("/analyze-quiz-ab-test/{quiz_id}")
async def analyze_quiz_ab_test(
    quiz_id: int,
    model_name: str = "azure",
    current_user=Depends(get_current_user)
):
    """
    Generate input data and analyze quiz answers for the specified student and quiz
    using both prompt versions for A/B testing comparison.

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

        # Get all questions and student responses for this quiz from table (temporary)
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
        
        # Prepare questions_and_answers structure for prompt generator v3
        questions_and_answers_v3 = []
        for response in ai_responses:
            questions_and_answers_v3.append({
                "question_id": response.question_id,
                "question_text": response.question_text,
                "student_answer_text": response.answer.get('text', ''),
                "lecturer_answer_text": response.lecturer_answer_text,
                "rubric": response.rubric,
                "rubric_max_score": response.rubric_max_score
            })
        
        # Prepare questions_and_answers structure for prompt generator b
        # Note: prompt_generator_b uses 'max_score' instead of 'rubric_max_score'
        questions_and_answers_for_b = []
        for response in ai_responses:
            questions_and_answers_for_b.append({
                "question_id": response.question_id,
                "question_text": response.question_text,
                "student_answer_text": response.answer.get('text', ''),
                "lecturer_answer_text": response.lecturer_answer_text,
                "max_score": response.rubric_max_score # Use rubric_max_score as max_score for prompt_b
            })

        # Generate analysis prompt for v3
        prompt_v3 = construct_overall_assignment_analysis_prompt_v3(
            quiz_id=quiz.id,
            student_id=current_user.id,
            model_name=model_name,
            questions_and_answers=questions_and_answers_v3,
            overall_assignment_title=quiz.title,
            lecturer_overall_notes=quiz.lecturer_overall_notes
        )
        
        # Generate analysis prompt for v3_b
        prompt_v3_b = construct_model_answer_comparison_prompt_b(
            quiz_id=quiz.id,
            student_id=current_user.id,
            model_name=model_name,
            questions_and_answers=questions_and_answers_for_b,
            overall_assignment_title=quiz.title,
            lecturer_overall_notes=quiz.lecturer_overall_notes
        )
        
        # Get LLM API call function
        llm_call_function = get_llm_api_call_function(model_name)

        # Analyze with LLM for both prompts
        analysis_result_v3, input_tokens_v3 = llm_call_function(prompt_v3)
        analysis_result_v3_b, input_tokens_v3_b = llm_call_function(prompt_v3_b)

        print("Analysis Result V3:", analysis_result_v3)
        print("Analysis Result V3_B:", analysis_result_v3_b)
        print("Input Tokens V3:", input_tokens_v3)
        print("Input Tokens V3_B:", input_tokens_v3_b)
        
        # Return both analysis results for comparison
        return {
            "success": True,
            "analysis_v3": analysis_result_v3,
            "analysis_v3_b": analysis_result_v3_b,
            "model_used": model_name,
            "quiz_id": quiz.id,
            "student_id": current_user.id,
            "input_tokens_v3": input_tokens_v3, # Add input tokens for v3
            "input_tokens_v3_b": input_tokens_v3_b # Add input tokens for v3_b
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions with their original status code
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quiz analysis failed: {str(e)}"
        )

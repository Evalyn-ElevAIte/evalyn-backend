from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import IntegrityError
from app.models.models import QuestionResponse, Question, QuizParticipant, Quiz
from app.schemas.question_response import (
    QuestionResponseCreate,
    QuestionResponseRead,
    BulkQuestionResponseCreate,
    QuestionResponseToAI,
    BulkQuestionResponseToAI
)
from app.schemas.quiz import QuizReadWithQuestions
from app.schemas.question import QuestionReadForStudent
from app.dependencies import get_current_user
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List

router = APIRouter()

StudentResponse = pydantic_model_creator(QuestionResponse, name="QuestionResponse")

@router.get("/quiz/{quiz_id}", response_model=QuizReadWithQuestions)
async def get_quiz_with_questions(
    quiz_id: int,
    current_user=Depends(get_current_user)
):
    # Check if quiz exists
    quiz = await Quiz.get_or_none(id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check if user is participant in the quiz
    participant = await QuizParticipant.get_or_none(
        user_id=current_user.id,
        quiz_id=quiz_id
    )
    if not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant in this quiz"
        )

    # Get all questions for the specified quiz
    questions = await Question.filter(quiz_id=quiz_id)
    await quiz.fetch_related('creator')
    
    return QuizReadWithQuestions(
        id=quiz.id,
        title=quiz.title,
        creator_id=quiz.creator.id,
        description=quiz.description,
        join_code=quiz.join_code,
        created_at=quiz.created_at,
        duration=quiz.duration,
        questions=[
            QuestionReadForStudent(
                id=q.id,
                quiz_id=q.quiz_id,
                text=q.text,
                type=q.type,
                options=q.options,
                created_at=q.created_at
            ) for q in questions
        ]
    )

@router.post("/", response_model=List[QuestionResponseRead])
async def submit_all_answers(
    bulk_response_data: BulkQuestionResponseCreate,
    current_user=Depends(get_current_user)
):
    # Check if quiz exists
    quiz = await Quiz.get_or_none(id=bulk_response_data.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check if user is participant in the quiz
    participant = await QuizParticipant.get_or_none(
        user_id=current_user.id,
        quiz_id=bulk_response_data.quiz_id
    )
    if not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant in this quiz"
        )
    
    # Update participant status to submitted
    participant.status = "submited"
    await participant.save()

    # Get all questions for the specified quiz
    quiz_questions = await Question.filter(quiz_id=bulk_response_data.quiz_id)
    valid_question_ids = {q.id for q in quiz_questions}

    submitted_responses = []
    for response_data in bulk_response_data.responses:
        # Validate if the question_id belongs to the specified quiz
        if response_data.question_id not in valid_question_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Question with ID {response_data.question_id} does not belong to Quiz ID {bulk_response_data.quiz_id}"
            )

        try:
            # Create response
            response = await QuestionResponse.create(
                user_id=current_user.id,
                question_id=response_data.question_id,
                answer=response_data.answer
            )
            await response.fetch_related('question')
            submitted_responses.append(
                QuestionResponseRead(
                    id=response.id,
                    question_id=response.question.id,
                    question_text=response.question.text,
                    question_type=response.question.type,
                    answer=response.answer,
                    joined_at=response.joined_at
                )
            )
        except IntegrityError:
            print(f"User {current_user.id} has already answered question {response_data.question_id}. Skipping.")
            pass
    
    if not submitted_responses:
        raise HTTPException(status_code=400, detail="No new answers were submitted or all were duplicates.")

    return submitted_responses


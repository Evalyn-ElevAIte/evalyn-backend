from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class QuestionResponseBase(BaseModel):
    question_id: int = Field(..., description="ID of the question being answered")
    answer: List[str] = Field(..., description="Student's answer as a List")

class QuestionResponseToAI(QuestionResponseBase):
    question_text: str = Field(..., description="Text of the question being answered")
    question_type: str = Field(..., description="Type of the question (e.g., multiple choice, open-ended)")
    lecturer_answer_text: List[str] = Field(None, description="Lecturer's answer to the question")
    rubric: Optional[str] = Field(None, description="Rubric for grading the question")
    rubric_max_score: Optional[int] = Field(None, description="Maximum score for the rubric")

class QuestionResponseCreate(QuestionResponseBase):
    pass

class QuestionResponseRead(QuestionResponseBase):
    id: int
    question_id: int = Field(..., description="ID of the question being answered")
    joined_at: datetime
    
    class Config:
        from_attributes = True

class BulkQuestionResponseCreate(BaseModel):
    quiz_id: int = Field(..., description="ID of the quiz for which answers are being submitted")
    title: str = Field(..., description="Title of the quiz")
    description: str = Field(..., description="Description of the quiz")
    responses: List[QuestionResponseCreate] = Field(..., description="List of student responses")

class BulkQuestionResponseToAI(BaseModel):
    quiz_id: int = Field(..., description="ID of the quiz for which answers are being submitted")
    title: str = Field(None, description="Title of the quiz")
    description: str = Field(None, description="Description of the quiz")
    lecturer_overall_notes: Optional[str] = Field(None, description="Overall notes from the lecturer")
    student_id: int = Field(...,description = "User ID")
    responses: List[QuestionResponseToAI] = Field(..., description="List of student responses")

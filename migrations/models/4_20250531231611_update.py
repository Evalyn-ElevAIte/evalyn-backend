from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_assessments" ALTER COLUMN "question_id" TYPE INT USING "question_id"::INT;
        ALTER TABLE "quizparticipant" ALTER COLUMN "status" TYPE VARCHAR(14) USING "status"::VARCHAR(14);
        COMMENT ON COLUMN "quizparticipant"."status" IS 'UNFINISHED: unfinished
SUBMITED: submited
GRADED: graded
AI_ANALYZED: Analyzed by AI';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "quizparticipant"."status" IS 'UNFINISHED: unfinished
SUBMITED: submited
GRADED: graded';
        ALTER TABLE "quizparticipant" ALTER COLUMN "status" TYPE VARCHAR(10) USING "status"::VARCHAR(10);
        ALTER TABLE "question_assessments" ALTER COLUMN "question_id" TYPE VARCHAR(100) USING "question_id"::VARCHAR(100);"""

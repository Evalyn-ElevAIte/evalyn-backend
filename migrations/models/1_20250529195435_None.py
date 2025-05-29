from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(128) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "quiz" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(64) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "lecturer_overall_notes" TEXT,
    "join_code" VARCHAR(10) NOT NULL UNIQUE,
    "completed" BOOL NOT NULL DEFAULT False,
    "start_time" TIMESTAMPTZ,
    "end_time" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "assessments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "submission_timestamp_utc" TIMESTAMPTZ NOT NULL,
    "assessment_timestamp_utc" TIMESTAMPTZ NOT NULL,
    "overall_score" INT NOT NULL DEFAULT 0,
    "overall_max_score" INT NOT NULL DEFAULT 0,
    "summary_of_performance" TEXT,
    "general_positive_feedback" TEXT,
    "general_areas_for_improvement" TEXT,
    "overall_scoring_confidence" DECIMAL(3,2),
    "feedback_generation_confidence" DECIMAL(3,2),
    "model_used" VARCHAR(50),
    "prompt_version" VARCHAR(100),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "quiz_id" INT NOT NULL REFERENCES "quiz" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_assessments_submiss_70d685" ON "assessments" ("submission_timestamp_utc");
CREATE INDEX IF NOT EXISTS "idx_assessments_assessm_088f1b" ON "assessments" ("assessment_timestamp_utc");
COMMENT ON TABLE "assessments" IS 'Main assessment model';
CREATE TABLE IF NOT EXISTS "question" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "type" VARCHAR(13) NOT NULL DEFAULT 'text',
    "options" JSONB,
    "expected_answer" JSONB,
    "rubric" TEXT NOT NULL,
    "rubric_max_score" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "quiz_id" INT NOT NULL REFERENCES "quiz" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "question"."type" IS 'TEXT: text\nMULTI_CHOICE: multi_choice\nSINGLE_CHOICE: single_choice';
CREATE TABLE IF NOT EXISTS "question_assessments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "question_id" VARCHAR(100) NOT NULL,
    "question_text" TEXT NOT NULL,
    "student_answer_text" TEXT,
    "lecturer_answer_text" TEXT,
    "rubric" TEXT,
    "rubric_max_score" INT NOT NULL DEFAULT 0,
    "score" INT NOT NULL DEFAULT 0,
    "max_score_possible" INT NOT NULL DEFAULT 0,
    "overall_question_feedback" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "assessment_id" INT NOT NULL REFERENCES "assessments" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_question_as_assessm_8911b1" ON "question_assessments" ("assessment_id", "question_id");
COMMENT ON TABLE "question_assessments" IS 'Question assessment model';
CREATE TABLE IF NOT EXISTS "missing_concepts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "missing_concept" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "question_assessment_id" INT NOT NULL REFERENCES "question_assessments" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "missing_concepts" IS 'Missing concepts in student answer model';
CREATE TABLE IF NOT EXISTS "questionresponse" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "answer" JSONB NOT NULL,
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "question_id" INT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_questionres_user_id_36bdac" UNIQUE ("user_id", "question_id")
);
CREATE TABLE IF NOT EXISTS "quizparticipant" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(10) NOT NULL,
    "score" INT NOT NULL DEFAULT 0,
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "quiz_id" INT NOT NULL REFERENCES "quiz" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_quizpartici_user_id_fa0430" UNIQUE ("user_id", "quiz_id")
);
COMMENT ON COLUMN "quizparticipant"."status" IS 'UNFINISHED: unfinished\nSUBMITED: submited\nGRADED: graded';
CREATE TABLE IF NOT EXISTS "rubric_component_feedback" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "component_description" VARCHAR(255) NOT NULL,
    "component_evaluation" TEXT,
    "component_strengths" TEXT,
    "component_areas_for_improvement" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "question_assessment_id" INT NOT NULL REFERENCES "question_assessments" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "rubric_component_feedback" IS 'Rubric component feedback model';
CREATE TABLE IF NOT EXISTS "student_key_points" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key_point" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "question_assessment_id" INT NOT NULL REFERENCES "question_assessments" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "student_key_points" IS 'Key points covered by student model';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

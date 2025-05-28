from fastapi import FastAPI, Depends
from app.db.db import init_db, close_db
from app.routes import quiz, user, userAuth, questions

app = FastAPI()

app.include_router(userAuth.router, prefix="/api/auth", tags=["userAuth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

# startup
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
def read_root():
    return {"message" : "welcome brother"}

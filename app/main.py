from fastapi import FastAPI
from app.routes import quiz

app = FastAPI()
app.include_router(quiz.router)

@app.get("/")
def read_root():
    return {"message" : "welcome brother"}


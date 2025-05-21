from fastapi import FastAPI
from app.db.db import init_db, close_db
from app.routes import quiz

app = FastAPI()
app.include_router(quiz.router)

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


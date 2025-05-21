# Evalyn Backend
Focus on routing, modelling, database configurations, data manipulations, and AI


## 🛠️ Setup Instructions

1. Create and activate your virtual environment:
    ```
    python -m venv evalyn_env 
    # On Windows: evalyn_env\Scripts\activate
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. If you add new libraries/dependencies during development, update the requirements file:
    ```
    pip freeze > requirements.txt
    ```
Keeping this file updated ensures that everyone on the team is using the same dependencies. ✅

4. **Start The Server**
    ```
    uvicorn app.main:app --reload
    ```

## 📁 Project Structure
project-root/
- app/                 # Main application folder
  - routes/           # FastAPI route files (e.g., quiz.py, user.py)
  - models/           # Pydantic or SQLAlchemy models
  - services/         # Business logic (e.g., quiz grading, user management)
  - ai/               # Azure AI integrations (e.g., OpenAI, Form Recognizer)
  - db/               # Database connections and queries
  - main.py           # Entry point for the FastAPI app
- evalyn_env/         # Virtual environment (ignored by Git)
- .gitignore          # Git ignore rules
- requirements.txt    # Python dependencies
- README.md           # Project documentation

## API Documentation (pending)
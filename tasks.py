import os

def run():
    os.system("uvicorn main:app --reload")

def seed():
    os.system("python -m app.seed")

if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else None
    if task == "run":
        run()
    elif task == "seed":
        seed()
    else:
        print("Usage: python tasks.py [run|seed]")

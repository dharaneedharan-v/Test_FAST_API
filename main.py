from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "FastAPI compiled flawlessly via uv!"}
@app.get("/home")
def hello():
    return {"message": "Hello, FastAPI!"}






#  help full commands 
# To run the application: 
            # uv run uvicorn main:app --reload

        # uv export --no-hashes --no-dev --format requirements-txt > requirements.txt
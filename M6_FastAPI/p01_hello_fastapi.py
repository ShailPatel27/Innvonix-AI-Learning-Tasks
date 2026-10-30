# run using: 
# uvicorn  p01_hello_fastapi:app --reload
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

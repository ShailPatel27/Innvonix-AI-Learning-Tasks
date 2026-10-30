from typing import Annotated

from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/login")
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    return {"username": username, "password_length": len(password)}

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserPublic(BaseModel):
    username: str
    email: str


class UserRecord(UserPublic):
    password: str


@app.get("/users/{user_id}", response_model=UserPublic)
def read_user(user_id: int):
    return UserRecord(
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password="this-field-is-not-returned",
    )

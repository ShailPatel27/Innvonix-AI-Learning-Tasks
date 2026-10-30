from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Response

app = FastAPI()


@app.get("/client-info")
def read_client_info(
    user_agent: Annotated[str | None, Header()] = None,
    session_id: Annotated[str | None, Cookie()] = None,
):
    return {"user_agent": user_agent, "session_id": session_id}


@app.post("/start-session")
def start_session(response: Response):
    response.set_cookie(key="session_id", value="demo-session", httponly=True)
    return {"message": "Session started"}

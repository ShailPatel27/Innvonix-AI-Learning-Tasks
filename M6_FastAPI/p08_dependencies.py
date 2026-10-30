from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


def common_parameters(search: str | None = None, page: int = 1, page_size: int = 10):
    return {"search": search, "page": page, "page_size": page_size}


@app.get("/items")
def read_items(params: Annotated[dict, Depends(common_parameters)]):
    return {"filters": params, "items": []}


@app.get("/users")
def read_users(params: Annotated[dict, Depends(common_parameters)]):
    return {"filters": params, "users": []}

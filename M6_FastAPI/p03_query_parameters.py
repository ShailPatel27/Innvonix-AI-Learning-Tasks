from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()

items = ["keyboard", "mouse", "monitor", "webcam", "headphones"]


@app.get("/items")
def read_items(
    search: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    results = items
    if search:
        results = [item for item in items if search.lower() in item.lower()]
    return results[skip : skip + limit]

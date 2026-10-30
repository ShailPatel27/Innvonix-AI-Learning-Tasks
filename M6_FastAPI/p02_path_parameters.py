from fastapi import FastAPI

app = FastAPI()

items = {1: "Keyboard", 2: "Mouse", 3: "Monitor"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": items.get(item_id, "Unknown item")}

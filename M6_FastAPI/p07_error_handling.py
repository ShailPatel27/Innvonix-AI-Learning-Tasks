from fastapi import FastAPI, HTTPException

app = FastAPI()

books = {1: "The Hobbit", 2: "Pride and Prejudice"}


@app.get("/books/{book_id}")
def read_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"id": book_id, "title": books[book_id]}

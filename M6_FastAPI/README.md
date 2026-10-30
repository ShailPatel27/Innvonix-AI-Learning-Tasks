# FastAPI

Numbered examples introduce API development with FastAPI. Each Python file defines a separate app.

- `p01`-`p03`: first endpoints, path parameters, and query parameters
- `p04`-`p07`: request bodies, response models, status codes, and errors
- `p08`-`p13`: dependencies, headers and cookies, forms, file uploads, background tasks, and middleware
- `p14`: an in-memory CRUD API for tasks

Run an example from the repository root:

```bash
uv run uvicorn p01_hello_fastapi:app --app-dir M6_FastAPI --reload
```

Open `http://127.0.0.1:8000/docs` to explore its interactive API documentation. The examples use in-memory data, which resets when the app restarts.

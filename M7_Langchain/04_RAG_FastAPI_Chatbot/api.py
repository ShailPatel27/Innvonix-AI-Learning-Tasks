from io import BytesIO
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from pypdf import PdfReader
from langchain_core.documents import Document

from rag_service import add_documents, answer_question, indexed_chunk_count, indexed_documents

APP_DIR = Path(__file__).resolve().parent
app = FastAPI(title="LangChain RAG Chatbot", version="1.0.0")
chat_sessions: dict[str, list[dict[str, str]]] = {}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class Source(BaseModel):
    file: str
    page: int | None = None
    excerpt: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source]


def read_uploaded_file(filename: str, content: bytes) -> list[Document]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        pdf = PdfReader(BytesIO(content))
        documents = [
            Document(
                page_content=page.extract_text() or "",
                metadata={"page": page_number},
            )
            for page_number, page in enumerate(pdf.pages, start=1)
        ]
    elif suffix in {".txt", ".md"}:
        text = content.decode("utf-8-sig").strip()
        documents = [Document(page_content=text, metadata={"page": 1})] if text else []
    else:
        raise ValueError("Only PDF, TXT, and Markdown files are supported.")

    documents = [document for document in documents if document.page_content.strip()]
    if not documents:
        raise ValueError("No readable text was found in this file.")
    return documents


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/knowledge-base")


@app.get("/knowledge-base", include_in_schema=False)
def knowledge_base_page():
    return FileResponse(APP_DIR / "knowledge_base.html")


@app.get("/chatbot", include_in_schema=False)
def chatbot_page():
    return FileResponse(APP_DIR / "chatbot.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/documents")
def list_documents():
    try:
        chunk_count = indexed_chunk_count()
        documents = indexed_documents()
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"indexed_chunks": chunk_count, "documents": documents}


@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_documents(files: Annotated[list[UploadFile], File()]):
    if not files:
        raise HTTPException(status_code=400, detail="Choose at least one file.")

    results = []
    for file in files:
        filename = Path(file.filename or "upload.txt").name
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"{filename} is larger than 15 MB.")

        try:
            documents = read_uploaded_file(filename, content)
            chunk_count = add_documents(documents, filename)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=f"{filename}: {error}") from error
        except RuntimeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(
                status_code=502,
                detail=f"Could not process {filename}: {error}",
            ) from error

        results.append({"file": filename, "chunks_added": chunk_count})

    return {
        "files": results,
        "indexed_chunks": indexed_chunk_count(),
        "documents": indexed_documents(),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if indexed_chunk_count() == 0:
            raise HTTPException(
                status_code=409,
                detail="Upload at least one document before starting a RAG chat.",
            )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    session_id = request.session_id or str(uuid4())
    history = chat_sessions.setdefault(session_id, [])

    try:
        answer, sources = answer_question(request.question, history)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"The model request failed: {error}") from error

    history.extend(
        [
            {"role": "user", "content": request.question},
            {"role": "assistant", "content": answer},
        ]
    )
    chat_sessions[session_id] = history[-20:]
    return ChatResponse(session_id=session_id, answer=answer, sources=sources)


@app.delete("/chat/{session_id}")
def clear_chat(session_id: str):
    chat_sessions.pop(session_id, None)
    return {"message": "Chat history cleared."}

# FastAPI RAG Chatbot

Upload PDF, TXT, or Markdown documents and chat with them. LangChain splits and embeds the text, Chroma stores the chunks, and Gemini retrieves relevant passages and answers with source references. The browser chat page is served by FastAPI.

## Setup

Install the repository dependencies from the root:

```bash
uv sync
```

Set `GOOGLE_API_KEY` in the environment or in `M7_Langchain/.env`.

## Run

From the repository root:

```bash
uv run uvicorn api:app --app-dir M7_Langchain/04_RAG_FastAPI_Chatbot --reload
```

Open `http://127.0.0.1:8000` for the chatbot or `http://127.0.0.1:8000/docs` to explore the API.

Upload the included `sample_docs/rag_basics.txt` in the chat page to try the RAG flow. Uploaded chunks are persisted in `.chroma_db`; chat history is kept in memory and clears when the server restarts.

Document text is sent to Google for embeddings and chat responses. Do not upload sensitive material.

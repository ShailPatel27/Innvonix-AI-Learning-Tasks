# Enterprise Knowledge Platform

A configurable company knowledge assistant. Employees sign in, upload documents, choose which groups can access them, and chat with the documents available to their groups. Administrators create groups, assign employees, and review activity.

## Included in this version

- Employee signup and login with revocable 30-day sliding sessions that persist across browser restarts
- Admin role bootstrapped from environment settings; public signup cannot create an admin
- Admin-managed groups and memberships
- PDF, DOCX, XLSX, XLSM, CSV, TXT, and Markdown ingestion
- LangGraph workflow for contextual query rewriting, group-filtered Chroma retrieval, and source-linked Gemini answers
- Persistent document metadata, original uploads, and conversation history in local SQLite/storage
- Audit events for account, group, document, and chat activity
- A responsive browser dashboard served by FastAPI, with an employee and admin workspace
- An alternate Streamlit workspace with Overview, Assistant, Knowledge Base, and Administration pages

## Setup

Copy `M10_Enterprise_Knowledge_Platform/.env.example` to `M10_Enterprise_Knowledge_Platform/.env`, then set a Google AI API key and a unique admin password of at least 8 characters. The first server start creates the configured admin account. New signups are employees and need an administrator to add them to groups before they can access group documents.

Install dependencies from the repository root:

```bash
uv sync
```

Start the application from the repository root:

```bash
uv run uvicorn backend.api:app --app-dir M10_Enterprise_Knowledge_Platform --reload
```

Open `http://127.0.0.1:8000` for the workspace dashboard. API documentation is at `http://127.0.0.1:8000/docs`.

To use the Streamlit interface instead, start it from the repository root in another terminal:

```bash
uv run streamlit run M10_Enterprise_Knowledge_Platform/frontend/app.py
```

## First use

1. Sign in as the administrator configured in `.env`.
2. Create groups such as HR, Finance, and Engineering.
3. Employees create their own accounts, then the administrator assigns them to groups.
4. Upload a sample document and select one or more groups to share it with.
5. Sign in as a member of those groups and ask the assistant questions about the shared content.

The sample policies in `sample_docs/` contain synthetic data and can be uploaded through the interface.

## Access rules

- New accounts always receive the employee role.
- Only administrators can create groups or change group membership.
- Employees can upload documents only to groups they belong to.
- Retrieval searches only chunks tagged for groups the signed-in user currently belongs to. The API applies this filter, not only the interface.
- Administrators can access documents shared with any group. A document can be deleted by its uploader or an administrator.
- Conversation history is private to its owner. Audit logs record activity without storing chat prompts.

## Storage and provider

SQLite metadata and original uploads live under the ignored `data/` directory. Chroma vectors live under `data/chroma/`. Conversation history is kept in SQLite. Document text is sent to Google for embeddings and answer generation; avoid uploading sensitive company data to this learning deployment.

The browser keeps the signed-in session token in local storage and reuses it after refresh or restart. Server sessions expire after 30 days of inactivity and refresh as the user makes authenticated requests; signing out revokes the current session.

This is a local capstone prototype. It demonstrates the core access model and RAG flow; production use would need a managed identity system, HTTPS, malware scanning, backups, retention controls, and deployment-specific security review.

## Next extension points

- MCP connectors for company databases, email, and calendars
- LangGraph workflows for multi-step analysis and approval-gated actions
- Department dashboards, report generation, and workflow analytics

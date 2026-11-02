# LangGraph and Agentic AI

This module explores how to build stateful AI workflows with LangGraph. The examples cover validation, chatbots, tools, multi-agent workflows, and retrieval.

## Setup

From the repository root, install the project dependencies:

```bash
uv sync
```

Copy `M9_LangGraph/.env.example` to `M9_LangGraph/.env`, then add `GOOGLE_API_KEY` for examples that use Gemini. LangSmith tracing is optional. The Typesense example also needs a running Typesense server and an API key.

Run an example from the repository root:

```bash
uv run python M9_LangGraph/02_Graph_Fundamentals/01_state_graph.py
```

## Modules

### 1. Pydantic Validation
- Validate fields and related values with Pydantic.
- Ask a model for structured output that follows a schema.

### 2. Graph Fundamentals
- Pass shared state through graph nodes.
- Route requests with conditional edges.
- Keep chat history with a checkpointer and thread ID.

### 3. Agentic Chatbots
- Let a model call typed Python tools and use their results in its response.

### 4. Debugging and Monitoring
- Stream graph updates while a workflow runs.
- Send traces to LangSmith when configured.

### 5. MCP Integration
- Create an MCP server with a few learning tools.
- Connect a LangGraph agent to an MCP server over standard input and output.

### 6. Multi-Agent Workflows
- Coordinate researcher, writer, and reviewer roles through a revision loop.

### 7. RAG Workflows
- Build a basic retrieval and answer graph.
- Split Markdown documents into chunks and store them in Chroma.
- Expand a question into multiple searches and combine the results.
- Review generated answers against retrieved evidence.

### 8. Multimodal RAG
- Extract text from PDFs and descriptions from images.
- Search both kinds of content in one vector store.

### 9. Typesense Retrieval
- Index sample Markdown documents and search them with Typesense.

## Suggested order

1. Start with Pydantic and graph fundamentals.
2. Continue through chatbots, monitoring, MCP, and multi-agent workflows.
3. For Chroma retrieval, run `02_ingest_and_retrieve.py` before `03_multi_query_retrieval.py` or `04_hallucination_guard.py`.
4. Add PDFs to `08_Multimodal_RAG/pdfs/` and images to `08_Multimodal_RAG/images/` before running its example.
5. Start Typesense before running its search example.

The Chroma examples use the included Markdown files in `07_RAG_Workflows/sample_docs/`. Vector data is saved locally under `M9_LangGraph/data/`.

## MCP example

Open two terminals from the repository root. Start the server in the first:

```bash
uv run python M9_LangGraph/05_MCP_Integration/01_learning_tools_server.py
```

Then run the agent in the second:

```bash
uv run python M9_LangGraph/05_MCP_Integration/02_mcp_tool_agent.py
```

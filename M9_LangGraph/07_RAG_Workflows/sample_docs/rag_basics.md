# Retrieval-Augmented Generation

Retrieval-augmented generation (RAG) combines search with language generation. A system first retrieves relevant passages, then gives those passages to a language model as context for an answer.

## Typical steps

1. Load source documents.
2. Split long documents into smaller chunks.
3. Create embeddings and store them in a vector database.
4. Embed the user's question and retrieve similar chunks.
5. Generate an answer from the question and retrieved context.

RAG can make answers more relevant to a private knowledge base. It does not guarantee that an answer is correct, so sources and evidence should still be checked.

## Retrieval quality

Chunk size, overlap, metadata, query rewriting, and reranking can all affect what the answer model receives. Evaluation should check both whether useful evidence was retrieved and whether the final answer is supported by that evidence.

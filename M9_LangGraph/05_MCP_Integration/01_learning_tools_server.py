from mcp.server.fastmcp import FastMCP

mcp = FastMCP("learning-tools")


@mcp.tool()
def lookup_topic(topic: str) -> str:
    """Look up a short explanation of a LangGraph learning topic."""
    topics = {
        "state": "State is the shared data passed between graph nodes.",
        "node": "A node is a function that reads state and returns state updates.",
        "edge": "An edge determines which node runs next.",
    }
    return topics.get(topic.lower(), "Topic not found. Try state, node, or edge.")


@mcp.tool()
def add_numbers(first: int, second: int) -> int:
    """Add two whole numbers."""
    return first + second


if __name__ == "__main__":
    mcp.run(transport="stdio")

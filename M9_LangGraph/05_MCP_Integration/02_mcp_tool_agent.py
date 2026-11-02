import asyncio
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model

SERVER_PATH = Path(__file__).with_name("01_learning_tools_server.py")


async def run_agent():
    server = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            @tool
            async def lookup_topic(topic: str) -> str:
                """Look up a short explanation of a LangGraph topic using the MCP server."""
                result = await session.call_tool("lookup_topic", {"topic": topic})
                return "\n".join(item.text for item in result.content if hasattr(item, "text"))

            @tool
            async def add_numbers(first: int, second: int) -> str:
                """Add two whole numbers using the MCP server."""
                result = await session.call_tool(
                    "add_numbers", {"first": first, "second": second}
                )
                return "\n".join(item.text for item in result.content if hasattr(item, "text"))

            tools = [lookup_topic, add_numbers]
            model = get_chat_model().bind_tools(tools)

            def call_model(state: MessagesState):
                return {"messages": [model.invoke(state["messages"])]}

            builder = StateGraph(MessagesState)
            builder.add_node("assistant", call_model)
            builder.add_node("tools", ToolNode(tools))
            builder.add_conditional_edges("assistant", tools_condition)
            builder.add_edge("tools", "assistant")
            builder.set_entry_point("assistant")
            graph = builder.compile()

            result = await graph.ainvoke(
                {"messages": [HumanMessage(content="What is a LangGraph node?")]}
            )
            print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run_agent())

"""A coroutine is an async function that can pause while waiting for work."""
import asyncio


async def greet(name: str) -> str:
    print(f"Preparing a greeting for {name}...")
    await asyncio.sleep(1)  # Simulates waiting for I/O without blocking the loop.
    return f"Hello, {name}!"


async def main() -> None:
    # Calling an async function creates a coroutine; awaiting it runs it.
    message = await greet("Shail")
    print(message)


if __name__ == "__main__":
    asyncio.run(main())

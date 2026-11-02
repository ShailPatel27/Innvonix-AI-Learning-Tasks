"""Manage related tasks together with Python 3.11 TaskGroup."""
import asyncio


async def process(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    print(f"Processed {name}")
    return f"done: {name}"


async def main() -> None:
    tasks: list[asyncio.Task[str]] = []
    async with asyncio.TaskGroup() as group:
        tasks.append(group.create_task(process("alpha", 0.4)))
        tasks.append(group.create_task(process("beta", 0.2)))
        tasks.append(group.create_task(process("gamma", 0.3)))

    # Exiting the TaskGroup waits for its tasks to finish.
    print("Results:", [task.result() for task in tasks])


if __name__ == "__main__":
    asyncio.run(main())

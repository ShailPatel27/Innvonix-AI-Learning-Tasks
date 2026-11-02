"""Create tasks to schedule coroutines, then await every task."""
import asyncio


async def download(label: str, delay: float) -> str:
    print(f"{label}: started")
    await asyncio.sleep(delay)
    print(f"{label}: complete")
    return f"{label} data"


async def main() -> None:
    # create_task schedules each coroutine so it can progress when this task awaits.
    task_a = asyncio.create_task(download("A", 1.0), name="download-A")
    task_b = asyncio.create_task(download("B", 0.5), name="download-B")

    print("Both downloads have been scheduled")
    results = await asyncio.gather(task_a, task_b)
    print("Results:", results)


if __name__ == "__main__":
    asyncio.run(main())

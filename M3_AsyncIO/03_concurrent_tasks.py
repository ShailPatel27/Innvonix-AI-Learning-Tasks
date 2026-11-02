"""Run independent coroutines concurrently with asyncio.gather."""
import asyncio
import time


async def fetch_item(item_id: int) -> str:
    print(f"Starting item {item_id}")
    await asyncio.sleep(1)
    print(f"Finished item {item_id}")
    return f"item-{item_id}"


async def main() -> None:
    started = time.perf_counter()
    results = await asyncio.gather(
        fetch_item(1),
        fetch_item(2),
        fetch_item(3),
    )
    print("Results:", results)
    print(f"Elapsed: {time.perf_counter() - started:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())

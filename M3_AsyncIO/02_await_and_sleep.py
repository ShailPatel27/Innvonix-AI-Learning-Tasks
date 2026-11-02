"""Awaiting work and yielding control during simulated I/O."""
import asyncio


async def fetch_item(item_id: int) -> str:
    print(f"Starting item {item_id}")
    await asyncio.sleep(1)
    print(f"Finished item {item_id}")
    return f"item-{item_id}"


async def main() -> None:
    # These calls are awaited one after another, so their waits add up.
    first = await fetch_item(1)
    second = await fetch_item(2)
    print("Results:", first, second)


if __name__ == "__main__":
    asyncio.run(main())

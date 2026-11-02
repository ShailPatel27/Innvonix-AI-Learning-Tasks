"""Set a deadline for async work and clean up cancelled tasks."""
import asyncio


async def slow_operation() -> str:
    try:
        print("Operation started")
        await asyncio.sleep(5)
        return "operation complete"
    finally:
        # finally also runs when asyncio cancels the coroutine.
        print("Operation cleanup finished")


async def main() -> None:
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=1)
        print(result)
    except TimeoutError:
        print("The operation exceeded its 1 second deadline")


if __name__ == "__main__":
    asyncio.run(main())

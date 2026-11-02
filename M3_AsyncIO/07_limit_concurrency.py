"""Use a semaphore to limit how many operations run at once."""
import asyncio


async def request(number: int, limit: asyncio.Semaphore) -> str:
    async with limit:
        print(f"Request {number} started")
        await asyncio.sleep(0.5)
        print(f"Request {number} finished")
        return f"response-{number}"


async def main() -> None:
    limit = asyncio.Semaphore(2)
    results = await asyncio.gather(
        *(request(number, limit) for number in range(1, 6))
    )
    print("Results:", results)


if __name__ == "__main__":
    asyncio.run(main())

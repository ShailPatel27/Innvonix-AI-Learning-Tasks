"""Pass work to a fixed number of async workers using asyncio.Queue."""
import asyncio


async def worker(name: str, jobs: asyncio.Queue[int | None]) -> None:
    while True:
        job = await jobs.get()
        try:
            if job is None:  # Sentinel tells this worker to exit.
                print(f"{name} stopping")
                return
            print(f"{name} processing job {job}")
            await asyncio.sleep(0.3)
            print(f"{name} completed job {job}")
        finally:
            jobs.task_done()


async def main() -> None:
    jobs: asyncio.Queue[int | None] = asyncio.Queue()
    workers = [
        asyncio.create_task(worker(f"worker-{index}", jobs))
        for index in range(1, 4)
    ]

    for job in range(1, 7):
        await jobs.put(job)

    await jobs.join()  # Wait until every submitted job has been acknowledged.
    for _ in workers:
        await jobs.put(None)
    await asyncio.gather(*workers)
    print("All jobs processed")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import time
 
 
async def timecalc(worker):
    start_time = time.time()
    await worker()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
 
async def func1():
    for i in range(1, 6):
        await asyncio.sleep(1)
        print(f"Count: {i}")
 
async def func2():
    for i in range(6, 11):
        await asyncio.sleep(1)
        print(f"Count: {i}")
 
async def func3():
    for i in range(11, 16):
        await asyncio.sleep(1)
        print(f"Count: {i}")
 
async def func4():
    for i in range(16, 21):
        await asyncio.sleep(1)
        print(f"Count: {i}")

async def func5():
    print("func5")
 
async def main():
    # await func3()
    task1 = asyncio.create_task(func1())
    task2 = asyncio.create_task(func2())
    # await asyncio.gather(func1(), func2())
    # asyncio.create_task(func4())
    await func4()
    print(asyncio.all_tasks())
    print("Running........")
    await func5()
 
 
if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Total elapsed time: {time.time() - start:.10f} seconds")
 
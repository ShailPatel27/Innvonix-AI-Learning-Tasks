# AsyncIO

This module moves from basic coroutines to coordinating concurrent work. The examples use only Python's standard library and require Python 3.11 or newer.

Run any lesson from the repository root:

```bash
uv run python M3_AsyncIO/01_coroutines.py
```

## Suggested learning path

1. **`01_coroutines.py`** - Define an `async def` coroutine, await it, and start an event loop with `asyncio.run`.
2. **`02_await_and_sleep.py`** - See how `await` pauses a coroutine and how sequential waits work.
3. **`03_concurrent_tasks.py`** - Run independent coroutines concurrently with `asyncio.gather`.
4. **`04_create_and_await_tasks.py`** - Schedule work with `asyncio.create_task`, then collect results and ensure tasks finish.
5. **`challenge_create_task.py`** - Reason through several basic asyncio concepts interacting in a less obvious way.
6. **`05_task_group.py`** - Manage related work with the structured-concurrency `TaskGroup` API.
7. **`06_timeout_and_cancellation.py`** - Apply a deadline and handle cancellation cleanup.
8. **`07_limit_concurrency.py`** - Use a semaphore to cap simultaneous operations.
9. **`08_queue_worker_pool.py`** - Build a producer/worker pattern with a queue and a fixed worker pool.

## Challenge: task scheduling and output order

The challenge is not an advanced topic. It combines familiar ideas from the earlier lessons: `create_task`, directly awaiting a coroutine, `sleep` yielding control, and inspecting active tasks. Before running it, predict which counters can interleave, when the created tasks finish, and what `asyncio.all_tasks()` includes at that point. The exercise is to explain the output from the scheduling interactions.

## Key ideas

- AsyncIO is most useful for I/O-bound work that can wait without blocking, such as network requests or file/database operations supported by async libraries.
- `await` yields control only when the awaited operation cooperates with the event loop. A long CPU-bound loop still blocks other coroutines.
- Creating a task schedules work, but the program must still await or otherwise manage that task. Unfinished tasks can be cancelled when the event loop closes.
- Concurrency does not automatically make CPU-heavy Python code faster. Use processes or an appropriate native/library implementation for CPU-bound work.

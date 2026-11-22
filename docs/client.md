# AssetClient library guide

The simulated upstream has variable response times and supports concurrent reads.
You may edit this client in Part 3; treat `AssetStore` as the external service.

## Methods

`client.fetch(asset_id)` blocks until a lookup finishes. It returns a record
dictionary or `None` when the ID is unknown.

`client.fetch_many(asset_ids)` performs concurrent lookups with up to four
workers. Its intended contract is one record or `None` per input ID, in request
order. The implementation has not yet been fully verified.

## Concurrency primitives used here

`ThreadPoolExecutor(max_workers=4)` runs submitted callables on worker threads.
`executor.submit(fn, arg)` immediately returns a Future representing that call.

`future.result()` waits if needed, then returns the callable's return value.
If the callable raised an exception, `result()` raises that exception.

`as_completed(futures)` yields Futures as they finish, regardless of submission
order. A Future may already be complete when iteration begins.

Leaving the executor's `with` block waits for submitted work to finish.

For this exercise, unknown IDs return `None`. Timeouts and retries are discussion
topics, not implementation requirements.

# Asset Lookup: learning interview practice

An original 45–60 minute practice exercise, inspired by public descriptions of
Palantir's learning interview. This is not an actual Palantir interview question.

You have joined a team maintaining an asset lookup service. A dashboard currently
calls `GET /assets/{id}` once per asset. Your task is to add a batch endpoint,
then investigate a report that asset cards sometimes appear in the wrong order.

## Start here

Python 3.9+; no installations or external services needed.

```sh
python3 -m unittest tests.test_single -v
python3 server.py
```

In another terminal:

```sh
curl http://127.0.0.1:8000/assets/A-100
curl -X POST http://127.0.0.1:8000/assets/batch \
  -H 'Content-Type: application/json' \
  -d '{"asset_ids":["A-100","A-200","A-300"]}'
```

The single endpoint works. The batch endpoint initially returns 501 because it
is your implementation task. The upstream client's batch method already exists,
but has a deliberate defect. No solutions are included.

## Part 1: understand the system (10 minutes)

Read `docs/client.md`, `handlers.py`, and `upstream.py`.
Explain the path from an HTTP request to an asset record and back.
What is a Future? What does `result()` do? What happens for an unknown asset?

## Part 2: add batching (15 minutes)

Implement `batch_assets()` in `handlers.py`. Begin with the existing single-item
lookup. Use the contract in `docs/api.md`; preserve the single endpoint.

```sh
python3 -m unittest tests.test_batch -v
```

## Part 3: improve latency and debug (20 minutes)

The dashboard often requests 10 assets. A sequential implementation spends most
of its time waiting. Update your handler to use `AssetClient.fetch_many()`.

Now reproduce the customer's report:

```sh
python3 demo.py
python3 -m unittest tests.test_client_batch -v
python3 -m unittest discover -v
```

The IDs printed by the demo may differ from the request order. Investigate the
client implementation and fix the underlying defect. Keep concurrent lookups,
preserve one result per input position, and keep all contract tests passing.
Do not change the simulated upstream delays to make the tests pass.

Before editing, state your hypothesis and describe an experiment that tests it.
Afterward, add a regression test of your own and explain why your fix works.

## Part 4: discuss (5–10 minutes)

- Why might a one-item batch hide the bug?
- How should duplicates, missing records, and an empty batch behave?
- What if one lookup raises a timeout instead of returning a missing record?
- How would you limit the work if many clients send batches simultaneously?
- Should a future API return an ID-keyed map or an ordered list? What changes?

## Files

| File | Role |
| --- | --- |
| `handlers.py` | Existing single endpoint and your batch implementation |
| `upstream.py` | Simulated upstream and client library |
| `server.py` | Small HTTP adapter; no framework knowledge needed |
| `docs/api.md` | HTTP contract |
| `docs/client.md` | Client library documentation |
| `demo.py` | Reproduces the response-order symptom |
| `tests/` | Contract and regression tests |

Initial test failures are intentional: batch handler tests fail until Part 2,
and client ordering tests expose the defect for Part 3.

## Background reading

Public candidate reports describe reading unfamiliar code or documentation and
then extending or debugging a system. Exact interview content varies.

- https://www.glassdoor.com/Interview/Palantir-Technologies-Interview-Questions-E236375.htm?filter.jobTitleExact=Software+Engineer%28Internship%29
- https://www.jointaro.com/interviews/companies/palantir/experiences/software-engineer-denver-co-january-1-2025-no-offer-neutral-7f3868e6/

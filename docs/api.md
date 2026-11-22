# HTTP contract

## GET /assets/{asset_id}

Existing behavior: 200 for a known asset, 404 for an unknown asset.

```json
{"asset_id":"A-100","status":"ok","asset":{"id":"A-100","name":"Water pump","site":"Madrid"}}
```

Missing response:

```json
{"asset_id":"A-999","status":"not_found","asset":null}
```

## POST /assets/batch

Input:

```json
{"asset_ids":["A-300","A-100","A-999","A-300"]}
```

Return HTTP 200 and `{"results": [...]}` for every valid batch, including one
where every asset is missing. Each element has the same body shape as a single
lookup. A missing asset is a per-item result, not a whole-request 404.

Requirements:

- Result at index `i` corresponds to input at index `i`.
- Duplicates remain separate output entries.
- Missing assets retain their positions.
- An empty list returns `{"results": []}`.
- At most 25 IDs per request.
- Return 400 with an `error` string for invalid input: body must be an object,
  `asset_ids` must be a list, and each ID must be a nonempty string.
- Ignore extra object fields. Do not mutate the request body.

The HTTP adapter handles malformed JSON. Endpoint handlers receive parsed JSON
and return a `Response(status_code, body)` object.

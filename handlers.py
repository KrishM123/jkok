"""Application handlers. Implement the batch endpoint here."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from upstream import AssetClient


@dataclass
class Response:
    status_code: int
    body: Dict[str, Any]


def asset_result(asset_id: str, asset: Optional[dict]) -> dict:
    return {
        "asset_id": asset_id,
        "status": "ok" if asset is not None else "not_found",
        "asset": asset,
    }


def get_asset(asset_id: str, client: AssetClient) -> Response:
    asset = client.fetch(asset_id)
    return Response(200 if asset is not None else 404, asset_result(asset_id, asset))


def batch_assets(body: Any, client: AssetClient) -> Response:
    # Part 2: implement docs/api.md, initially using single lookups.
    # Part 3: switch to the batch client and investigate the reported defect.
    raise NotImplementedError("Implement POST /assets/batch")

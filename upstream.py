"""Simulated external store and an existing client library."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Sequence


class AssetStore:
    def __init__(self, simulate_latency: bool = True):
        self.simulate_latency = simulate_latency
        self._assets = {
            "A-100": {"id": "A-100", "name": "Water pump", "site": "Madrid"},
            "A-200": {"id": "A-200", "name": "Generator", "site": "Seville"},
            "A-300": {"id": "A-300", "name": "Cooling unit", "site": "Bilbao"},
            "A-400": {"id": "A-400", "name": "Pressure sensor", "site": "Madrid"},
        }
        self._delays = {"A-100": 0.12, "A-200": 0.01, "A-300": 0.06, "A-400": 0.03}

    def lookup(self, asset_id: str) -> Optional[Dict[str, str]]:
        if self.simulate_latency:
            time.sleep(self._delays.get(asset_id, 0.02))
        asset = self._assets.get(asset_id)
        return dict(asset) if asset is not None else None


class AssetClient:
    def __init__(self, store: Optional[AssetStore] = None):
        self.store = store if store is not None else AssetStore()

    def fetch(self, asset_id: str) -> Optional[Dict[str, str]]:
        return self.store.lookup(asset_id)

    def fetch_many(self, asset_ids: Sequence[str]) -> List[Optional[Dict[str, str]]]:
        with ThreadPoolExecutor(max_workers=4) as executor:
            pending = [executor.submit(self.fetch, asset_id) for asset_id in asset_ids]
            return [future.result() for future in as_completed(pending)]

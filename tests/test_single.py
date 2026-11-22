import unittest

from handlers import get_asset
from upstream import AssetClient, AssetStore


class SingleTests(unittest.TestCase):
    def setUp(self):
        self.client = AssetClient(AssetStore(simulate_latency=False))

    def test_known_asset(self):
        result = get_asset("A-100", self.client)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body["asset"]["name"], "Water pump")
        self.assertEqual(result.body["status"], "ok")

    def test_missing_asset(self):
        result = get_asset("A-999", self.client)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.body, {"asset_id": "A-999", "status": "not_found", "asset": None})

    def test_records_are_independent(self):
        self.client.fetch("A-100")["name"] = "Changed"
        self.assertEqual(self.client.fetch("A-100")["name"], "Water pump")

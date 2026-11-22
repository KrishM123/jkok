import copy
import unittest

from handlers import batch_assets, get_asset
from upstream import AssetClient, AssetStore


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.client = AssetClient(AssetStore(simulate_latency=False))

    def check_batch(self, ids):
        response = batch_assets({"asset_ids": ids}, self.client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, {
            "results": [get_asset(asset_id, self.client).body for asset_id in ids]
        })

    def test_request_order(self):
        self.check_batch(["A-300", "A-100", "A-200"])

    def test_duplicates_and_missing(self):
        self.check_batch(["A-300", "A-999", "A-100", "A-300", "A-999"])

    def test_empty(self):
        self.check_batch([])

    def test_all_missing(self):
        self.check_batch(["unknown", "another"])

    def test_maximum_batch(self):
        self.check_batch(["A-200"] * 25)

    def test_invalid_input(self):
        for body in [None, [], "bad", {}, {"asset_ids": None},
                     {"asset_ids": "A-100"}, {"asset_ids": [12]},
                     {"asset_ids": [True]}, {"asset_ids": [""]},
                     {"asset_ids": ["A-100"] * 26}]:
            with self.subTest(body=body):
                response = batch_assets(body, self.client)
                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.body.get("error"), str)

    def test_input_unchanged_and_extra_fields_ignored(self):
        body = {"asset_ids": ["A-300", "A-100", "A-300"], "trace": "abc"}
        before = copy.deepcopy(body)
        response = batch_assets(body, self.client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, before)

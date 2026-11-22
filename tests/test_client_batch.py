import threading
import unittest
from concurrent.futures import wait
from unittest.mock import patch

from upstream import AssetClient, AssetStore


def completed_in_reverse(futures):
    # All work may finish before a caller starts consuming completions. In that
    # case any iteration order is legal. Exercise one adversarial legal order.
    futures = list(futures)
    wait(futures)
    yield from reversed(futures)


class ConcurrentStore(AssetStore):
    def __init__(self):
        super().__init__(simulate_latency=False)
        self.barrier = threading.Barrier(4)

    def lookup(self, asset_id):
        try:
            self.barrier.wait(timeout=2)
        except threading.BrokenBarrierError:
            raise AssertionError("Four lookups must be able to run concurrently")
        return super().lookup(asset_id)


class ClientBatchTests(unittest.TestCase):
    def assert_ordered(self, ids):
        client = AssetClient(AssetStore(simulate_latency=False))
        with patch("upstream.as_completed", completed_in_reverse):
            actual = client.fetch_many(ids)
        expected = [client.fetch(asset_id) for asset_id in ids]
        self.assertEqual(actual, expected)

    def test_out_of_order_completion(self):
        self.assert_ordered(["A-100", "A-200", "A-300"])

    def test_missing_keeps_its_position(self):
        self.assert_ordered(["A-100", "A-999", "A-200"])

    def test_duplicate_keeps_each_position(self):
        self.assert_ordered(["A-100", "A-200", "A-100", "A-300"])

    def test_lookups_overlap(self):
        records = AssetClient(ConcurrentStore()).fetch_many(
            ["A-100", "A-200", "A-300", "A-400"]
        )
        self.assertCountEqual([record["id"] for record in records],
                              ["A-100", "A-200", "A-300", "A-400"])

    def test_empty(self):
        self.assertEqual(AssetClient().fetch_many([]), [])

    def test_one_item(self):
        client = AssetClient(AssetStore(simulate_latency=False))
        self.assertEqual(client.fetch_many(["A-300"]), [client.fetch("A-300")])

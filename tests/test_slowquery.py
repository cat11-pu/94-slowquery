import unittest

from slowapi import Monitor
from slowquery import Tracker


class TestTracker(unittest.TestCase):
    def test_record_counts(self):
        self.assertEqual(Tracker().record("select 1", 10)["records"], 1)

    def test_records_shape(self):
        tracker = Tracker()
        tracker.record("select 1", 10)
        self.assertEqual(tracker.records[0], ("select 1", 10))

    def test_stats_shape(self):
        self.assertIn("threshold", Tracker().stats())

    def test_empty_records(self):
        self.assertEqual(Tracker().records, [])

    def test_monitor_wraps_tracker(self):
        monitor = Monitor()
        monitor.record("select 1", 10)
        self.assertEqual(monitor.tracker.stats()["records"], 1)


if __name__ == "__main__":
    unittest.main()

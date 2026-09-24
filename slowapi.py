"""slowapi.py：对外门面（老接口 record 不能改）。"""
from __future__ import annotations

from slowquery import Tracker


class Monitor:
    def __init__(self, threshold: int = 100, top: int = 2, sample_every: int = 2):
        self.tracker = Tracker(threshold, top, sample_every)

    def record(self, sql: str, millis: int) -> dict:
        return self.tracker.record(sql, millis)

    def fingerprint(self, sql: str) -> str:
        return self.tracker.fingerprint(sql)

    def slowest(self) -> list:
        return self.tracker.slowest()

    def snapshot(self) -> bytes:
        return self.tracker.persist()

    def rebuild(self, blob: bytes = None) -> dict:
        return self.tracker.restore(blob)

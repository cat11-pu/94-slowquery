"""slowquery.py：慢查询（基线：全量记录）。"""
from __future__ import annotations


class Tracker:
    def __init__(self, threshold: int = 100, top: int = 2, sample_every: int = 2):
        self.threshold = threshold
        self.top = top
        self.sample_every = sample_every
        self.records = []
        self.seen = 0
        self.dropped = 0

    def record(self, sql: str, millis: int) -> dict:
        """基线：全都记下来。"""
        self.records.append((sql, millis))
        return {"records": len(self.records)}

    def fingerprint(self, sql: str) -> str:
        raise NotImplementedError("指纹归并还没实现")

    def slowest(self) -> list:
        raise NotImplementedError("Top-K 还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"records": len(self.records), "seen": self.seen, "dropped": self.dropped,
                "threshold": self.threshold, "top": self.top, "sample_every": self.sample_every}

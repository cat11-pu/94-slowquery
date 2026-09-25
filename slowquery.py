"""slowquery.py：慢查询（指纹归并 + 采样 + Top-K + 快照）。"""
from __future__ import annotations

import json
import re

_PLACEHOLDER_PATTERN = re.compile(r"'[^']*'|\d+")


class Tracker:
    def __init__(self, threshold: int = 100, top: int = 2, sample_every: int = 2):
        self.threshold = threshold
        self.top = top
        self.sample_every = sample_every
        self.records = []
        self.seen = 0
        self.dropped = 0
        self._total = 0
        self._stats = {}

    def record(self, sql: str, millis: int) -> dict:
        """按指纹归并统计，并按 sample_every 采样保留明细。"""
        self._total += 1
        fp = self.fingerprint(sql)
        entry = self._stats.get(fp)
        if entry is None:
            self._stats[fp] = [millis, 1]
        else:
            if millis > entry[0]:
                entry[0] = millis
            entry[1] += 1
        if self.sample_every <= 1 or self._total % self.sample_every == 1:
            self.records.append((sql, millis))
            self.seen += 1
        else:
            self.dropped += 1
        return {"records": len(self.records)}

    def fingerprint(self, sql: str) -> str:
        """数字与单引号字符串替换为占位符 ?。"""
        return _PLACEHOLDER_PATTERN.sub("?", sql)

    def slowest(self) -> list:
        """Top-K：仅最大耗时严格超过阈值的指纹，按最大耗时降序、指纹升序。"""
        candidates = [(fp, entry[0]) for fp, entry in self._stats.items()
                      if entry[0] > self.threshold]
        candidates.sort(key=lambda item: (-item[1], item[0]))
        return [[fp, millis] for fp, millis in candidates[:self.top]]

    def persist(self) -> bytes:
        payload = {
            "threshold": self.threshold,
            "top": self.top,
            "sample_every": self.sample_every,
            "stats": self._stats,
            "records": self.records,
            "seen": self.seen,
            "dropped": self.dropped,
            "total": self._total,
        }
        return json.dumps(payload).encode("utf-8")

    def restore(self, blob: bytes = None) -> dict:
        if blob is not None:
            payload = json.loads(blob.decode("utf-8"))
            self.threshold = payload["threshold"]
            self.top = payload["top"]
            self.sample_every = payload["sample_every"]
            self._stats = {fp: list(entry) for fp, entry in payload["stats"].items()}
            self.records = [tuple(item) for item in payload["records"]]
            self.seen = payload["seen"]
            self.dropped = payload["dropped"]
            self._total = payload["total"]
        return {"kept": len(self.records), "seen": self.seen, "dropped": self.dropped,
                "fingerprints": len(self._stats)}

    def stats(self) -> dict:
        return {"records": len(self.records), "seen": self.seen, "dropped": self.dropped,
                "threshold": self.threshold, "top": self.top, "sample_every": self.sample_every,
                "fingerprints": len(self._stats)}

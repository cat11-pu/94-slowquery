"""check_sample.py：按 sample/queries.json 走一圈，打印验收面。"""
import json
import os
import sys

from slowquery import Tracker


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "queries.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    tracker = Tracker(spec["threshold"], spec["top"], spec["sample_every"])
    fingerprints = []
    for item in spec["queries"]:
        fingerprints.append(tracker.fingerprint(item["sql"]))
        tracker.record(item["sql"], item["millis"])
    slowest = tracker.slowest()
    blob = tracker.persist()
    reborn = Tracker(spec["threshold"], spec["top"], spec["sample_every"])
    restored = reborn.restore(blob)
    print("指纹序列 =", fingerprints)
    print("不同指纹数 =", len(set(fingerprints)))
    print("Top-K 慢查询 =", slowest)
    print("采样保留的条数 =", tracker.stats().get("seen"))
    print("采样丢弃的条数 =", tracker.stats().get("dropped"))
    print("恢复后的保留条数 =", restored.get("kept"))
    print("不变量（Top-K 只含超过阈值的） =", spec["threshold_invariant"])
    print("查询条数 =", len(spec["queries"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

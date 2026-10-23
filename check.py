#!/usr/bin/env python3
"""Validate JSONL AI-search observations; keep missing data out of mention rates."""
import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

STATUSES = {"completed", "failed", "timeout", "skipped"}


def validate(row):
    if not isinstance(row, dict):
        raise ValueError("record must be an object")
    for key in ("id", "engine", "language", "prompt_id", "observed_at"):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    stamp = dt.datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    if row.get("status") not in STATUSES:
        raise ValueError("invalid status")
    if row["status"] == "completed":
        if type(row.get("brand_mentioned")) is not bool:
            raise ValueError("completed requires boolean brand_mentioned")
    elif row.get("brand_mentioned") is not None:
        raise ValueError("unavailable observations must not assert brand_mentioned")
    return row


def summarize(rows):
    counts = Counter(row["status"] for row in rows)
    completed = counts["completed"]
    mentions = sum(row.get("brand_mentioned") is True for row in rows)
    return {
        "records": len(rows),
        "by_status": {status: counts[status] for status in sorted(STATUSES)},
        "completed_observations": completed,
        "mentions_in_completed_observations": mentions,
        "observed_mention_rate": mentions / completed if completed else None,
        "completion_fraction": completed / len(rows) if rows else None,
        "limitation": "Descriptive sample only; not market share, causal lift, or search ranking.",
    }


def load(path):
    rows, seen = [], set()
    for number, line in enumerate(Path(path).read_text(encoding="utf8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = validate(json.loads(line))
            if row["id"] in seen:
                raise ValueError("duplicate observation id")
            seen.add(row["id"])
            rows.append(row)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"line {number}: {exc}") from exc
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="UTF-8 JSONL file")
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(load(args.file)), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

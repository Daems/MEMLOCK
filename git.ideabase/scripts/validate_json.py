#!/usr/bin/env python3
"""Tiny syntax validator for CSRS git.ideabase JSON files.

This checks that schema and fixture JSON files parse. It intentionally does not
perform full JSON Schema validation, keeping the repo dependency-free.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "schemas" / "validation_run_record.schema.json",
    ROOT / "schemas" / "method_failure_event.schema.json",
    ROOT / "tests" / "fixtures" / "validation_run_record.example.json",
    ROOT / "tests" / "fixtures" / "method_failure_event.example.json",
]


def main() -> int:
    failed = False
    for path in TARGETS:
        try:
            json.loads(path.read_text(encoding="utf-8"))
            print(f"OK {path.relative_to(ROOT)}")
        except Exception as exc:
            failed = True
            print(f"FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

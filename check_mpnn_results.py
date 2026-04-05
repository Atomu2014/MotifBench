#!/usr/bin/env python3
"""Check that each run under output_ppflow/10_7WRK has non-empty self_consistency/seqs."""

from __future__ import annotations

import sys
from pathlib import Path


def seqs_dir_nonempty(seqs: Path) -> tuple[bool, str]:
    if not seqs.exists():
        return False, "missing"
    if not seqs.is_dir():
        return False, "not a directory"
    files = [p for p in seqs.iterdir() if p.is_file()]
    if not files:
        return False, "no files"
    if not any(p.stat().st_size > 0 for p in files):
        return False, "only zero-byte files"
    return True, f"{len(files)} file(s), all non-empty check passed"


def main() -> int:
    # TASK_NAME = '10_7WRK'
    TASK_NAME = sys.argv[1]
    repo_root = Path(__file__).resolve().parent
    default_root = TASK_NAME
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_root

    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2

    subdirs = sorted(p for p in root.iterdir() if p.is_dir())
    if not subdirs:
        print(f"WARNING: no subdirectories under {root}", file=sys.stderr)
        return 1

    failures: list[tuple[str, str]] = []
    oks = 0

    for d in subdirs:
        seqs = d / "self_consistency" / "seqs"
        ok, detail = seqs_dir_nonempty(seqs)
        name = d.name
        if ok:
            oks += 1
            print(f"OK   {name}/self_consistency/seqs  ({detail})")
        else:
            failures.append((name, detail))
            print(f"FAIL {name}/self_consistency/seqs  ({detail})")

    print("---")
    print(f"Total subdirs: {len(subdirs)}  OK: {oks}  FAIL: {len(failures)}")

    if failures:
        print("\nFailed samples:", file=sys.stderr)
        for name, detail in failures:
            print(f"  {name}: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

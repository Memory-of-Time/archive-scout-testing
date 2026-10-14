#!/usr/bin/env python3
"""Read-only verification of the four v1.2.4 CI repair source files."""
from __future__ import annotations
import hashlib
from pathlib import Path

EXPECTED = {'archive_scout/cli.py': '0aedfeb636b2fbc75a4466c91f755bb1830c21a6bf56863ce80707ba5d3c7908', 'archive_scout/projects/backups.py': '4626c5d9a83a0517ed6f01255aae7e5e646c98f205b19076a6177480830d918b', 'archive_scout/projects/repair.py': '0e5fd6733b03b88477f2f24b0a0b59fd257b1292c0779b8e607183d7b3ba5cb1', 'archive_scout/ui/main_window.py': '3c130238fe5e0e6113194abc28f78d8e543a064e40027aa3e55d3a23cfcab9be'}
ROOT = Path(__file__).resolve().parent
failed = False
for relative, expected in EXPECTED.items():
    path = ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    okay = actual == expected
    print(("OK  " if okay else "BAD ") + relative + ("" if okay else " (missing or old revision)"))
    failed = failed or not okay
raise SystemExit(1 if failed else 0)

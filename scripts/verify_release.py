"""Cross-check the release version and workflow placement without external services."""
from __future__ import annotations
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    from archive_scout.constants import VERSION
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'(?m)^version\s*=\s*"' + re.escape(VERSION) + r'"', pyproject), "pyproject version"
    win_version = (root / "packaging/windows/version_info.txt").read_text(encoding="utf-8")
    assert "'" + VERSION + "'" in win_version, "Windows version"
    workflow = root / ".github/workflows/tests.yml"
    assert workflow.is_file(), "GitHub workflow missing"
    assert 'python scripts/run_tests.py' in workflow.read_text(encoding="utf-8"), "canonical test runner missing from CI"
    assert (root / "archive_scout/ui/main_window.py").is_file()
    print("Source release identity, packaging version, CI workflow and core files verified:", VERSION)
    return 0


if __name__ == "__main__":
    sys.exit(main())

Archive Scout v1.2.2 — Windows/macOS CI path-alias hotfix

Unzip into the repository root, preserving the tests/unit/ path.
Overwrite tests/unit/test_v121_v120_upgrade_compat.py.

Changes in that test (no application source changes):
- Compare relocated project directories with Path.samefile() instead of direct Path equality.
- Compare rebased saved document paths with Path.samefile() instead of direct Path equality.

Reason: macOS /var vs /private/var and Windows 8.3 RUNNER~1 vs runneradmin
refer to the same physical locations but have different textual spellings.
The test still fails if the relocated directory or saved body does not exist.

Target: archive-scout-testing action run 38312052527, v1.2.2 plus prior missing resume script add-on.

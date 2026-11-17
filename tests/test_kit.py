# SPDX-License-Identifier: MIT
"""End to end: apply the template to a fresh repo, then check commitguard passes it and blocks a planted leak."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent


def run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


class KitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run(self.repo, "git", "init", "-q")
        applied = run(
            self.repo, sys.executable, str(KIT / "apply_template.py"),
            "--target", ".", "--project", "demo", "--owner", "Demo Org", "--contact", "https://example.com",
        )  # fmt: skip
        self.assertEqual(applied.returncode, 0, applied.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def guard(self) -> subprocess.CompletedProcess[str]:
        run(self.repo, "git", "add", "-A", "-f")
        return run(self.repo, sys.executable, "scripts/commitguard.py", "--all")

    def test_freshly_applied_template_passes_its_own_guard(self):
        self.assertTrue((self.repo / "LICENSE").exists())
        self.assertNotIn("{{", (self.repo / "COMMERCIAL.md").read_text(encoding="utf-8"))
        result = self.guard()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_guard_blocks_a_secret_and_model_weights(self):
        fake_key = "AKIA" + "ABCDEFGHIJKLMNOP"  # split so scanners don't flag this file
        (self.repo / "leak.py").write_text(f'# SPDX-License-Identifier: MIT\nKEY = "{fake_key}"\n', encoding="utf-8")
        (self.repo / "weights").mkdir()
        (self.repo / "weights" / "model.pt").write_bytes(b"x")
        result = self.guard()
        self.assertEqual(result.returncode, 1)
        self.assertIn("AWS access key", result.stderr)
        self.assertIn("weights/model.pt", result.stderr)


if __name__ == "__main__":
    unittest.main()

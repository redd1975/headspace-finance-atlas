import json
import pathlib
import tempfile
import unittest

from preview.build import build

class PreviewBuildTests(unittest.TestCase):
    def test_build_uses_only_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = pathlib.Path(temporary) / "site"
            build(42, "a" * 40, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            fixture = json.loads((out / "progress.json").read_text(encoding="utf-8"))
            manifest = json.loads((out / "preview-manifest.json").read_text(encoding="utf-8"))
            self.assertIn('data-hs-preview="synthetic"', html)
            self.assertEqual(fixture["test_data"], "synthetic")
            self.assertFalse(fixture["connected"])
            self.assertIsNone(fixture["verified_at"])
            self.assertEqual(manifest["pr_number"], 42)
            self.assertEqual(manifest["commit_sha"], "a" * 40)
            self.assertEqual(manifest["owner_acceptance"], "pending")
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["index.html", "preview-manifest.json", "progress.json"])

    def test_refuse_invalid_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            for pr, sha in [(0, "a" * 40), (5, "bad"), (4, "G" * 40)]:
                with self.assertRaises(ValueError):
                    build(pr, sha, pathlib.Path(temporary) / "out")

if __name__ == "__main__":
    unittest.main()

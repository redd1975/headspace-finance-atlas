import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from preview.build import build
from preview.verify import verify
from preview.cleanup import cleanup, PROJECT_ID

class PreviewVerifyTests(unittest.TestCase):
    def test_valid_synthetic_build(self):
        with tempfile.TemporaryDirectory() as t:
            path = pathlib.Path(t)
            build(27, "a" * 40, path)
            verify(path, 27, "a" * 40)
            with self.assertRaises(ValueError):
                verify(path, 27, "b" * 40)

    def test_reject_connected_data(self):
        with tempfile.TemporaryDirectory() as t:
            path = pathlib.Path(t)
            build(27, "a" * 40, path)
            f = path / "progress.json"
            data = json.loads(f.read_text())
            data["connected"] = True
            f.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "isolated"):
                verify(path, 27, "a" * 40)

class CleanupTests(unittest.TestCase):
    def test_only_same_pr_preview_project_removed(self):
        sample = {"deployments": [
            {"uid": "dpl_correct", "projectId": PROJECT_ID, "target": "preview", "meta": {"atlasPreviewPr": "42"}},
            {"uid": "dpl_other_pr", "projectId": PROJECT_ID, "target": "preview", "meta": {"atlasPreviewPr": "41"}},
            {"uid": "dpl_production", "projectId": PROJECT_ID, "target": "production", "meta": {"atlasPreviewPr": "42"}},
            {"uid": "dpl_other_project", "projectId": "prj_other", "target": "preview", "meta": {"atlasPreviewPr": "42"}},
            {"uid": "dpl_untagged", "projectId": PROJECT_ID, "target": "preview", "meta": {}}
        ], "pagination": {}}
        calls = []
        def fake(method, path, token):
            calls.append((method, path))
            return sample if method == "GET" else {}
        with patch("preview.cleanup.request", side_effect=fake):
            self.assertEqual(cleanup(42, "fake-synthetic-token"), 1)
        deleted = [path for method, path in calls if method == "DELETE"]
        self.assertEqual(len(deleted), 1)
        self.assertIn("dpl_correct", deleted[0])

    def test_refuse_missing_token(self):
        with self.assertRaises(ValueError):
            cleanup(10, "")

if __name__ == "__main__":
    unittest.main()

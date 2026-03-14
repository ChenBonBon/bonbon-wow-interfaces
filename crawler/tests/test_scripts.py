import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.fetch_run import run as run_fetch
from scripts.generate_run import run as run_generate


class ScriptsTest(unittest.TestCase):
    def test_generate_run_creates_manifest_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_file = temp_path / "tasks.json"
            task_file.write_text(
                json.dumps(
                    [
                        {
                            "task_id": "uncommon-head-cloth",
                            "enabled": True,
                            "quality": "uncommon",
                            "category": "armor",
                            "slot": "head",
                            "type": "cloth",
                            "query_filters": {},
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            manifest_path = run_generate([str(task_file), str(temp_path / "outputs")])

            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["task_count"], 1)
            self.assertEqual(manifest["tasks"][0]["task_id"], "uncommon-head-cloth")

    def test_fetch_run_consumes_manifest_and_writes_result(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "uncommon-head-cloth",
                                "status": "planned",
                                "url": "https://example.com/items/1",
                                "category": "armor",
                                "slot": "head",
                                "type": "cloth",
                                "quality": "uncommon",
                                "query_filters": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            processed_manifest_path = run_fetch(
                [str(manifest_path)],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
            )

            self.assertEqual(processed_manifest_path, manifest_path)
            self.assertTrue((temp_path / "uncommon-head-cloth.json").exists())
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")


if __name__ == "__main__":
    unittest.main()

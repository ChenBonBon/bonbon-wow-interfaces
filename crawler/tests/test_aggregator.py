import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.aggregator import build_unique_items, write_unique_items


class AggregatorTest(unittest.TestCase):
    def test_build_unique_items_reads_items_by_task_file_and_deduplicates(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = self._write_manifest(temp_path)
            (temp_path / "items.by-task.json").write_text(
                json.dumps(
                    {
                        "task-a": {
                            "task_id": "task-a",
                            "url": "https://example.com/a",
                            "items": [
                                {"itemId": 1001, "name": "Alpha Hood"},
                                {"itemId": 1002, "name": "Beta Hood"},
                            ],
                        },
                        "task-b": {
                            "task_id": "task-b",
                            "url": "https://example.com/b",
                            "items": [
                                {"itemId": 1002, "name": "Beta Hood Duplicate"},
                                {"itemId": 1003, "name": "Gamma Hood"},
                            ],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            unique_items = build_unique_items(manifest_path)

            self.assertEqual(
                unique_items,
                [
                    {"itemId": 1001, "name": "Alpha Hood"},
                    {"itemId": 1002, "name": "Beta Hood"},
                    {"itemId": 1003, "name": "Gamma Hood"},
                ],
            )

    def test_write_unique_items_writes_items_unique_json(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = self._write_manifest(temp_path)
            (temp_path / "items.by-task.json").write_text(
                json.dumps(
                    {
                        "task-a": {
                            "task_id": "task-a",
                            "url": "https://example.com/a",
                            "items": [
                                {"itemId": 1001, "name": "Alpha Hood"},
                                {"itemId": 1002, "name": "Beta Hood"},
                            ],
                        },
                        "task-b": {
                            "task_id": "task-b",
                            "url": "https://example.com/b",
                            "items": [
                                {"itemId": 1002, "name": "Beta Hood Duplicate"},
                            ],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            output_path = write_unique_items(manifest_path)

            self.assertEqual(output_path, temp_path / "items.unique.json")
            self.assertTrue(output_path.exists())
            output_items = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                output_items,
                [
                    {"itemId": 1001, "name": "Alpha Hood"},
                    {"itemId": 1002, "name": "Beta Hood"},
                ],
            )

    def _write_manifest(self, temp_path):
        manifest_path = temp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "run_id": "2026-03-14T15-30-00",
                    "generated_at": "2026-03-14T15:30:00+08:00",
                    "task_file": "tasks/example.json",
                    "task_count": 3,
                    "tasks": [
                        {"task_id": "task-a", "status": "fetched"},
                        {"task_id": "task-b", "status": "fetched"},
                        {"task_id": "task-c", "status": "failed"},
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return manifest_path


if __name__ == "__main__":
    unittest.main()

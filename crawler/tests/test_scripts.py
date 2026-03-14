import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.aggregate_run import run as run_aggregate
from scripts.export_lua import run as run_export_lua
from scripts.fetch_run import run as run_fetch
from scripts.generate_run import run as run_generate
from scripts.retry_failed_run import run as run_retry_failed
from scripts.run_all import run as run_all


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

    def test_aggregate_run_writes_unique_items_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "fetched"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "task-a.json").write_text(
                json.dumps(
                    {
                        "task_id": "task-a",
                        "url": "https://example.com/a",
                        "items": [
                            {"itemId": 1001, "name": "Alpha Hood"},
                            {"itemId": 1002, "name": "Beta Hood"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "task-b.json").write_text(
                json.dumps(
                    {
                        "task_id": "task-b",
                        "url": "https://example.com/b",
                        "items": [
                            {"itemId": 1002, "name": "Beta Hood Duplicate"},
                            {"itemId": 1003, "name": "Gamma Hood"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            output_path = run_aggregate([str(manifest_path)])

            self.assertEqual(output_path, temp_path / "items.unique.json")
            self.assertTrue(output_path.exists())
            output_items = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                output_items,
                [
                    {"itemId": 1001, "name": "Alpha Hood"},
                    {"itemId": 1002, "name": "Beta Hood"},
                    {"itemId": 1003, "name": "Gamma Hood"},
                ],
            )

    def test_retry_failed_run_only_retries_failed_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "planned-task", "status": "planned", "url": "https://example.com/planned"},
                            {"task_id": "failed-task", "status": "failed", "url": "https://example.com/failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            processed_manifest_path = run_retry_failed(
                [str(manifest_path)],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
            )

            self.assertEqual(processed_manifest_path, manifest_path)
            self.assertTrue((temp_path / "failed-task.json").exists())
            self.assertFalse((temp_path / "planned-task.json").exists())
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "planned")
            self.assertEqual(updated_manifest["tasks"][1]["status"], "fetched")

    def test_run_all_orchestrates_generate_fetch_and_aggregate(self):
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

            manifest_path = run_all(
                [str(task_file), str(temp_path / "outputs")],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
            )

            self.assertTrue(manifest_path.exists())
            self.assertTrue((manifest_path.parent / "uncommon-head-cloth.json").exists())
            self.assertTrue((manifest_path.parent / "items.unique.json").exists())
            unique_items = json.loads((manifest_path.parent / "items.unique.json").read_text(encoding="utf-8"))
            self.assertEqual(unique_items, [{"itemId": 2620, "name": "Augural Shroud"}])

    def test_export_lua_writes_lua_data_file_from_complete_manifest(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            items_unique_path = temp_path / "items.unique.json"
            output_path = temp_path / "DisenchantableByWowhead.lua"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "fetched"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            items_unique_path.write_text(
                json.dumps(
                    [
                        {"itemId": 1002, "name": "Beta Hood"},
                        {"itemId": 1001, "name": "Alpha Hood"},
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            written_path = run_export_lua([str(manifest_path), str(output_path)])

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("[1001] = true", output_path.read_text(encoding="utf-8"))

    def test_export_lua_rejects_incomplete_manifest(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            output_path = temp_path / "DisenchantableByWowhead.lua"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {"task_id": "task-a", "status": "failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.unique.json").write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "failed"):
                run_export_lua([str(manifest_path), str(output_path)])

            self.assertFalse(output_path.exists())

    def test_quickdisenchant_toc_includes_wowhead_data_file(self):
        toc_path = Path(__file__).resolve().parents[2] / "QuickDisenchant" / "QuickDisenchant.toc"
        toc_text = toc_path.read_text(encoding="utf-8")
        self.assertIn("DisenchantableByWowhead.lua", toc_text)


if __name__ == "__main__":
    unittest.main()

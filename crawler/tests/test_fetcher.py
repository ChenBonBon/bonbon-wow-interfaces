import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.fetcher import (
    extract_listviewitems_json,
    fetch_manifest_results,
    parse_items_from_html,
    retry_failed_manifest_results,
)


SAMPLE_HTML = """
<html>
<body>
<script>
var listviewitems = [{"id":2620,"name":"Augural Shroud","quality":2},{"id":2621,"name":"Cowl of Necromancy","quality":2}];
new Listview({data: listviewitems});
</script>
</body>
</html>
"""


class FetcherTest(unittest.TestCase):
    def test_extract_listviewitems_json_returns_array_text(self):
        array_text = extract_listviewitems_json(SAMPLE_HTML)
        self.assertEqual(
            array_text,
            '[{"id":2620,"name":"Augural Shroud","quality":2},{"id":2621,"name":"Cowl of Necromancy","quality":2}]',
        )

    def test_parse_items_from_html_returns_minimal_item_fields(self):
        items = parse_items_from_html(SAMPLE_HTML)
        self.assertEqual(
            items,
            [
                {"itemId": 2620, "name": "Augural Shroud"},
                {"itemId": 2621, "name": "Cowl of Necromancy"},
            ],
        )

    def test_fetch_manifest_results_writes_result_and_updates_status(self):
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
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon_2",
                                "query_filters": {"available_to_players_161": "yes"},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            fetch_manifest_results(
                manifest_path,
                fetch_url=lambda url: SAMPLE_HTML,
            )

            result_path = temp_path / "uncommon-head-cloth.json"
            self.assertTrue(result_path.exists())
            result_data = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result_data["task_id"], "uncommon-head-cloth")
            self.assertEqual(
                result_data["items"],
                [
                    {"itemId": 2620, "name": "Augural Shroud"},
                    {"itemId": 2621, "name": "Cowl of Necromancy"},
                ],
            )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")

    def test_fetch_manifest_results_marks_failed_when_fetch_errors(self):
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
                                "task_id": "rare-main-hand-dagger",
                                "status": "planned",
                                "url": "https://example.com/items/2",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
                                "quality": "rare_3",
                                "query_filters": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            def raise_error(_url):
                raise RuntimeError("network error")

            fetch_manifest_results(
                manifest_path,
                fetch_url=raise_error,
            )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "failed")
            self.assertFalse((temp_path / "rare-main-hand-dagger.json").exists())

    def test_retry_failed_manifest_results_only_retries_failed_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 3,
                        "tasks": [
                            {
                                "task_id": "planned-task",
                                "status": "planned",
                                "url": "https://example.com/planned",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon_2",
                                "query_filters": {},
                            },
                            {
                                "task_id": "failed-task",
                                "status": "failed",
                                "url": "https://example.com/failed",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon_2",
                                "query_filters": {},
                            },
                            {
                                "task_id": "fetched-task",
                                "status": "fetched",
                                "url": "https://example.com/fetched",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon_2",
                                "query_filters": {},
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            retry_failed_manifest_results(
                manifest_path,
                fetch_url=lambda _url: SAMPLE_HTML,
            )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "planned")
            self.assertEqual(updated_manifest["tasks"][1]["status"], "fetched")
            self.assertEqual(updated_manifest["tasks"][2]["status"], "fetched")
            self.assertTrue((temp_path / "failed-task.json").exists())
            self.assertFalse((temp_path / "planned-task.json").exists())

    def test_retry_failed_manifest_results_keeps_failed_status_when_retry_fails(self):
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
                                "task_id": "failed-task",
                                "status": "failed",
                                "url": "https://example.com/failed",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
                                "quality": "rare_3",
                                "query_filters": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            def raise_error(_url):
                raise RuntimeError("network error")

            retry_failed_manifest_results(
                manifest_path,
                fetch_url=raise_error,
            )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "failed")
            self.assertFalse((temp_path / "failed-task.json").exists())


if __name__ == "__main__":
    unittest.main()

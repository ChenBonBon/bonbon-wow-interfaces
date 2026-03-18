import json
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import core.fetcher as fetcher_module
from core.fetcher import (
    extract_listviewitems_json,
    fetch_manifest_results,
    parse_items_from_html,
    retry_failed_manifest_results,
    _sleep_before_fetch,
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

ZERO_RESULT_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="text">Your criteria did not match any items. </div>
</body>
</html>
"""

JS_OBJECT_LITERAL_HTML = """
<html>
<body>
<script>
var listviewitems = [{"id":187566,"name":"Arcsmasher","quality":3,firstseenpatch: 0,popularity:30}];
new Listview({data: listviewitems});
</script>
</body>
</html>
"""


class FetcherTest(unittest.TestCase):
    def test_fetch_manifest_results_aborts_after_ten_consecutive_failures(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            tasks = []
            for index in range(12):
                tasks.append(
                    {
                        "task_id": f"armor-uncommon-head_1-cloth_armor_1-{index}",
                        "status": "planned",
                        "url": f"https://example.com/items/{index}",
                        "category": "armor",
                        "slot": "head_1",
                        "type": "cloth_armor_1",
                        "quality": "uncommon",
                        "query_filters": {},
                    }
                )

            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T18-00-00",
                        "generated_at": "2026-03-18T18:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": len(tasks),
                        "tasks": tasks,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            log_lines = []

            with patch.object(fetcher_module, "FETCH_CONCURRENCY", 1):
                with self.assertRaisesRegex(RuntimeError, "连续失败"):
                    fetch_manifest_results(
                        manifest_path,
                        fetch_url=lambda _url: (_ for _ in ()).throw(RuntimeError("network error")),
                        sleep_before_fetch=lambda: None,
                        logger=log_lines.append,
                        timestamp_fn=lambda: "2026-03-18 18:00:00",
                    )

            report_path = temp_path / "run-report.json"
            self.assertTrue(report_path.exists())

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            statuses = [task["status"] for task in updated_manifest["tasks"]]
            self.assertEqual(statuses.count("failed"), 10)
            self.assertEqual(statuses.count("planned"), 2)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["aborted_due_to_consecutive_failures"])
            self.assertEqual(report["consecutive_failure_limit"], 10)
            self.assertEqual(report["failed_count"], 10)
            self.assertEqual(report["planned_count"], 2)
            self.assertIn(
                "[2026-03-18 18:00:00] ABORT consecutive_failures=10 limit=10",
                log_lines,
            )

    def test_fetch_manifest_results_resets_consecutive_failure_streak_after_success(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            tasks = []
            for index in range(12):
                tasks.append(
                    {
                        "task_id": f"weapon-rare-main_hand_21-daggers_15-{index}",
                        "status": "planned",
                        "url": f"https://example.com/items/{index}",
                        "category": "weapon",
                        "slot": "main_hand_21",
                        "type": "daggers_15",
                        "quality": "rare",
                        "query_filters": {},
                    }
                )

            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T18-00-00",
                        "generated_at": "2026-03-18T18:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": len(tasks),
                        "tasks": tasks,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            responses = [RuntimeError("network error")] * 9 + [SAMPLE_HTML] + [RuntimeError("network error")] * 2

            def fetch_with_sequence(_url):
                result = responses.pop(0)
                if isinstance(result, Exception):
                    raise result
                return result

            with patch.object(fetcher_module, "FETCH_CONCURRENCY", 1):
                fetch_manifest_results(
                    manifest_path,
                    fetch_url=fetch_with_sequence,
                    sleep_before_fetch=lambda: None,
                    logger=lambda _line: None,
                    timestamp_fn=lambda: "2026-03-18 18:00:00",
                )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            statuses = [task["status"] for task in updated_manifest["tasks"]]
            self.assertEqual(statuses.count("failed"), 11)
            self.assertEqual(statuses.count("fetched"), 1)
            self.assertFalse((temp_path / "run-report.json").exists())

    def test_fetch_manifest_results_logs_start_done_and_progress(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            tasks = []
            for index in range(10):
                tasks.append(
                    {
                        "task_id": f"weapon-rare-main_hand_21-daggers_15-{index}",
                        "status": "planned",
                        "url": f"https://example.com/items/{index}",
                        "category": "weapon",
                        "slot": "main_hand_21",
                        "type": "daggers_15",
                        "quality": "rare",
                        "query_filters": {},
                    }
                )

            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T10-00-00",
                        "generated_at": "2026-03-18T10:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": len(tasks),
                        "tasks": tasks,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            log_lines = []

            fetch_manifest_results(
                manifest_path,
                fetch_url=lambda _url: SAMPLE_HTML,
                sleep_before_fetch=lambda: None,
                logger=log_lines.append,
                timestamp_fn=lambda: "2026-03-18 12:00:00",
            )

            start_lines = [line for line in log_lines if " START " in line]
            done_lines = [line for line in log_lines if " DONE " in line]

            self.assertEqual(len(start_lines), 10)
            self.assertEqual(len(done_lines), 10)
            self.assertIn(
                "[2026-03-18 12:00:00] START weapon-rare-main_hand_21-daggers_15-0",
                log_lines,
            )
            self.assertIn(
                "[2026-03-18 12:00:00] DONE weapon-rare-main_hand_21-daggers_15-0 item_count=2",
                log_lines,
            )
            self.assertIn(
                "[2026-03-18 12:00:00] PROGRESS done=10/10 fetched=10 failed=0",
                log_lines,
            )

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

    def test_parse_items_from_html_returns_empty_list_for_zero_result_page(self):
        items = parse_items_from_html(ZERO_RESULT_HTML)
        self.assertEqual(items, [])

    def test_parse_items_from_html_parses_js_object_literal_payload(self):
        items = parse_items_from_html(JS_OBJECT_LITERAL_HTML)
        self.assertEqual(
            items,
            [
                {"itemId": 187566, "name": "Arcsmasher"},
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
                                "quality": "uncommon",
                                "query_filters": {"available_to_players": "yes"},
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

    def test_fetch_manifest_results_treats_zero_result_page_as_success(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T20-00-00",
                        "generated_at": "2026-03-18T20:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "weapon-uncommon-main_hand_21-daggers_15",
                                "status": "planned",
                                "url": "https://example.com/items/zero",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
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

            fetch_manifest_results(
                manifest_path,
                fetch_url=lambda _url: ZERO_RESULT_HTML,
                sleep_before_fetch=lambda: None,
                logger=lambda _line: None,
                timestamp_fn=lambda: "2026-03-18 20:00:00",
            )

            result_path = temp_path / "weapon-uncommon-main_hand_21-daggers_15.json"
            result_data = json.loads(result_path.read_text(encoding="utf-8"))
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")
            self.assertNotIn("error_message", updated_manifest["tasks"][0])
            self.assertEqual(result_data["items"], [])

    def test_fetch_manifest_results_parses_js_object_literal_payload_as_success(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T20-10-00",
                        "generated_at": "2026-03-18T20:10:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "weapon-rare-main_hand_21-one_handed_maces_4",
                                "status": "planned",
                                "url": "https://example.com/items/js-object",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "one_handed_maces_4",
                                "quality": "rare",
                                "query_filters": {},
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
                fetch_url=lambda _url: JS_OBJECT_LITERAL_HTML,
                sleep_before_fetch=lambda: None,
                logger=lambda _line: None,
                timestamp_fn=lambda: "2026-03-18 20:10:00",
            )

            result_path = temp_path / "weapon-rare-main_hand_21-one_handed_maces_4.json"
            result_data = json.loads(result_path.read_text(encoding="utf-8"))
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")
            self.assertNotIn("error_message", updated_manifest["tasks"][0])
            self.assertEqual(
                result_data["items"],
                [{"itemId": 187566, "name": "Arcsmasher"}],
            )

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
                                "task_id": "weapon-rare-main_hand_21-daggers_15",
                                "status": "planned",
                                "url": "https://example.com/items/2",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
                                "quality": "rare",
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
            self.assertEqual(updated_manifest["tasks"][0]["error_message"], "network error")
            self.assertFalse((temp_path / "weapon-rare-main_hand_21-daggers_15.json").exists())

    def test_retry_failed_manifest_results_clears_stale_error_message_after_success(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T19-00-00",
                        "generated_at": "2026-03-18T19:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "failed-task",
                                "status": "failed",
                                "error_message": "HTTP Error 403: Forbidden",
                                "url": "https://example.com/failed",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
                                "quality": "rare",
                                "query_filters": {},
                            }
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
                sleep_before_fetch=lambda: None,
                logger=lambda _line: None,
                timestamp_fn=lambda: "2026-03-18 19:00:00",
            )

            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")
            self.assertNotIn("error_message", updated_manifest["tasks"][0])

    def test_fetch_manifest_results_logs_failures(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-18T10-00-00",
                        "generated_at": "2026-03-18T10:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "weapon-rare-main_hand_21-daggers_15",
                                "status": "planned",
                                "url": "https://example.com/items/2",
                                "category": "weapon",
                                "slot": "main_hand_21",
                                "type": "daggers_15",
                                "quality": "rare",
                                "query_filters": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            log_lines = []

            def raise_error(_url):
                raise RuntimeError("network error")

            fetch_manifest_results(
                manifest_path,
                fetch_url=raise_error,
                sleep_before_fetch=lambda: None,
                logger=log_lines.append,
                timestamp_fn=lambda: "2026-03-18 12:00:00",
            )

            self.assertIn(
                "[2026-03-18 12:00:00] START weapon-rare-main_hand_21-daggers_15",
                log_lines,
            )
            self.assertIn(
                "[2026-03-18 12:00:00] FAIL weapon-rare-main_hand_21-daggers_15",
                log_lines,
            )

    def test_fetch_manifest_results_uses_fixed_concurrency_of_three(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            tasks = []
            for index in range(6):
                tasks.append(
                    {
                        "task_id": f"task-{index}",
                        "status": "planned",
                        "url": f"https://example.com/items/{index}",
                        "category": "weapon",
                        "slot": "main_hand_21",
                        "type": "daggers_15",
                        "quality": "rare",
                        "query_filters": {},
                    }
                )

            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-16T10-00-00",
                        "generated_at": "2026-03-16T10:00:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": len(tasks),
                        "tasks": tasks,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            lock = threading.Lock()
            current_calls = 0
            peak_calls = 0

            def fetch_with_probe(_url):
                nonlocal current_calls, peak_calls
                with lock:
                    current_calls += 1
                    peak_calls = max(peak_calls, current_calls)
                time.sleep(0.05)
                with lock:
                    current_calls -= 1
                return SAMPLE_HTML

            fetch_manifest_results(
                manifest_path,
                fetch_url=fetch_with_probe,
                sleep_before_fetch=lambda: None,
            )

            self.assertEqual(peak_calls, 3)

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
                                "quality": "uncommon",
                                "query_filters": {},
                            },
                            {
                                "task_id": "failed-task",
                                "status": "failed",
                                "url": "https://example.com/failed",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon",
                                "query_filters": {},
                            },
                            {
                                "task_id": "fetched-task",
                                "status": "fetched",
                                "url": "https://example.com/fetched",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon",
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
                                "quality": "rare",
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

    def test_sleep_before_fetch_uses_random_delay_between_one_point_five_and_three_seconds(self):
        sleep_calls = []

        def fake_uniform(start, end):
            self.assertEqual(start, 1.5)
            self.assertEqual(end, 3.0)
            return 2.25

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        _sleep_before_fetch(rand_uniform=fake_uniform, sleep=fake_sleep)

        self.assertEqual(sleep_calls, [2.25])


if __name__ == "__main__":
    unittest.main()

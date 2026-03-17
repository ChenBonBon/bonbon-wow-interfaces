import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from core.runner import build_run_manifest, write_run_manifest


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.generated_at = datetime(2026, 3, 14, 15, 30, 0, tzinfo=timezone(timedelta(hours=8)))
        self.enabled_task = {
            "task_id": "uncommon-head-cloth",
            "enabled": True,
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "available_to_players": "yes",
                "can_be_worn_equipped": "yes",
            },
        }
        self.disabled_task = {
            "task_id": "weapon-rare-main_hand_21-daggers_15",
            "enabled": False,
            "quality": "rare",
            "category": "weapon",
            "slot": "main_hand_21",
            "type": "daggers_15",
        }

    def test_build_run_manifest_only_includes_enabled_tasks(self):
        with TemporaryDirectory() as temp_dir:
            task_file = self._write_task_file(temp_dir)

            manifest = build_run_manifest(task_file, generated_at=self.generated_at)

            self.assertEqual(manifest["run_id"], "2026-03-14T15-30-00")
            self.assertEqual(manifest["generated_at"], "2026-03-14T15:30:00+08:00")
            self.assertEqual(manifest["task_file"], str(task_file))
            self.assertEqual(manifest["task_count"], 1)
            self.assertEqual(len(manifest["tasks"]), 1)
            self.assertEqual(manifest["tasks"][0]["task_id"], "uncommon-head-cloth")
            self.assertEqual(manifest["tasks"][0]["status"], "planned")
            self.assertEqual(manifest["tasks"][0]["filter_path"], "quality:2/slot:1/type:1")
            self.assertEqual(manifest["tasks"][0]["query_string"], "filter=161:195;1:1;0:0")
            self.assertEqual(
                manifest["tasks"][0]["url"],
                "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=161:195;1:1;0:0",
            )

    def test_write_run_manifest_creates_output_directory_and_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_file = self._write_task_file(temp_dir)
            outputs_dir = temp_path / "outputs"

            manifest_path = write_run_manifest(
                task_file,
                outputs_dir=outputs_dir,
                generated_at=self.generated_at,
            )

            self.assertEqual(
                manifest_path,
                outputs_dir / "2026-03-14T15-30-00" / "manifest.json",
            )
            self.assertTrue(manifest_path.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_id"], "2026-03-14T15-30-00")
            self.assertEqual(manifest["task_count"], 1)
            self.assertEqual(manifest["tasks"][0]["task_id"], "uncommon-head-cloth")

    def _write_task_file(self, temp_dir):
        task_file = Path(temp_dir) / "tasks.json"
        task_file.write_text(
            json.dumps([self.enabled_task, self.disabled_task], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return task_file


if __name__ == "__main__":
    unittest.main()

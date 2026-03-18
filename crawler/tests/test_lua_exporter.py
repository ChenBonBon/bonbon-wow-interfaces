import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.lua_exporter import render_lua_item_id_table, write_lua_item_id_table


class LuaExporterTest(unittest.TestCase):
    def test_render_lua_item_id_table_outputs_sorted_item_ids(self):
        lua_text = render_lua_item_id_table(
            [
                {"itemId": 1002, "name": "Beta Hood"},
                {"itemId": 1001, "name": "Alpha Hood"},
            ]
        )

        self.assertEqual(
            lua_text,
            "QD = QD or _G.QuickDisenchantNS\nQD.WOWHEAD_NON_DISENCHANTABLE_ITEM_IDS = {\n  [1001] = true,\n  [1002] = true,\n}\n",
        )

    def test_write_lua_item_id_table_writes_target_file_when_manifest_is_complete(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            items_unique_path = temp_path / "items.unique.json"
            output_path = temp_path / "NonDisenchantableByWowhead.lua"
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

            written_path = write_lua_item_id_table(manifest_path, output_path=output_path)

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("[1001] = true", output_path.read_text(encoding="utf-8"))

    def test_write_lua_item_id_table_rejects_failed_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            (temp_path / "items.unique.json").write_text("[]", encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "failed"):
                write_lua_item_id_table(manifest_path)

    def test_write_lua_item_id_table_rejects_planned_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            (temp_path / "items.unique.json").write_text("[]", encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "planned"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "planned"):
                write_lua_item_id_table(manifest_path)


if __name__ == "__main__":
    unittest.main()

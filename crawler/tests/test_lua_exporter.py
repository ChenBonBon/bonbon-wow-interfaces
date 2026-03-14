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
            "QD = QD or _G.QuickDisenchantNS\nQD.WOWHEAD_DISENCHANTABLE_ITEM_IDS = {\n  [1001] = true,\n  [1002] = true,\n}\n",
        )

    def test_write_lua_item_id_table_writes_target_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            items_unique_path = temp_path / "items.unique.json"
            output_path = temp_path / "DisenchantableByWowhead.lua"
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

            written_path = write_lua_item_id_table(items_unique_path, output_path=output_path)

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("[1001] = true", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

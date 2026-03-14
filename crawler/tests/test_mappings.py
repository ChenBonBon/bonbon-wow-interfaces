import json
import unittest
from pathlib import Path

from core.mappings import (
    QUALITIES,
    SLOTS,
    build_task_slug,
    describe_task,
    get_category_type_meta,
    normalize_task,
    validate_task,
)


class MappingsTest(unittest.TestCase):
    def setUp(self):
        self.armor_task = {
            "task_id": "uncommon-head-cloth",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head",
            "type": "cloth",
        }
        self.weapon_task = {
            "task_id": "rare-main-hand-dagger",
            "quality": "rare",
            "category": "weapon",
            "slot": "main_hand",
            "type": "dagger",
        }

    def test_build_task_slug_uses_semantic_values(self):
        self.assertEqual(build_task_slug(self.armor_task), "uncommon-head-cloth")

    def test_describe_task_uses_chinese_labels(self):
        self.assertEqual(describe_task(self.armor_task), "绿色 头部 布甲")
        self.assertEqual(describe_task(self.weapon_task), "蓝色 主手 匕首")

    def test_normalize_task_adds_enabled_default(self):
        normalized = normalize_task(self.armor_task)
        self.assertTrue(normalized["enabled"])
        self.assertEqual(normalized["task_id"], "uncommon-head-cloth")

    def test_get_category_type_meta_returns_chinese_label(self):
        meta = get_category_type_meta("weapon", "dagger")
        self.assertEqual(meta["label"], "匕首")
        self.assertEqual(meta["wowhead"], {"facet": "type", "value": 15})

    def test_quality_and_slot_expose_wowhead_filter_metadata(self):
        self.assertEqual(QUALITIES["uncommon"]["wowhead"], {"facet": "quality", "value": 2})
        self.assertEqual(SLOTS["main_hand"]["wowhead"], {"facet": "slot", "value": 21})

    def test_validate_task_rejects_category_type_mismatch(self):
        invalid_task = dict(self.armor_task)
        invalid_task["type"] = "dagger"

        with self.assertRaises(ValueError):
            validate_task(invalid_task)

    def test_example_tasks_are_all_valid(self):
        config_path = Path(__file__).resolve().parents[1] / "tasks" / "wowhead_items.example.json"
        tasks = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertGreater(len(tasks), 0)
        for task in tasks:
            validate_task(task)


if __name__ == "__main__":
    unittest.main()

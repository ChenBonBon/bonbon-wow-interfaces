import unittest

from core.url_builder import build_task_url_parts


class UrlBuilderTest(unittest.TestCase):
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

    def test_builds_armor_url_parts(self):
        parts = build_task_url_parts(self.armor_task)
        self.assertEqual(parts["filter_path"], "quality:2/slot:1/type:1")
        self.assertEqual(parts["path"], "items/armor/quality:2/slot:1/type:1")
        self.assertEqual(parts["url"], "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1")

    def test_builds_weapon_url_parts(self):
        parts = build_task_url_parts(self.weapon_task)
        self.assertEqual(parts["filter_path"], "quality:3/slot:21/type:15")
        self.assertEqual(parts["path"], "items/weapons/quality:3/slot:21/type:15")
        self.assertEqual(parts["url"], "https://www.wowhead.com/items/weapons/quality:3/slot:21/type:15")


if __name__ == "__main__":
    unittest.main()

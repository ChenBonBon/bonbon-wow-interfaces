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
        self.query_filter_task = {
            "task_id": "uncommon-head-cloth-filtered",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head",
            "type": "cloth",
            "query_filters": {
                "available_to_players": "yes",
                "can_be_worn": "yes",
            },
        }
        self.single_query_filter_task = {
            "task_id": "uncommon-head-cloth-player",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head",
            "type": "cloth",
            "query_filters": {
                "available_to_players": "yes",
            },
        }
        self.any_query_filter_task = {
            "task_id": "uncommon-head-cloth-any",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head",
            "type": "cloth",
            "query_filters": {
                "available_to_players": "any",
                "can_be_worn": "yes",
            },
        }

    def test_builds_armor_url_parts(self):
        parts = build_task_url_parts(self.armor_task)
        self.assertEqual(parts["filter_path"], "quality:2/slot:1/type:1")
        self.assertEqual(parts["path"], "items/armor/quality:2/slot:1/type:1")
        self.assertEqual(parts["query_string"], "")
        self.assertEqual(parts["url"], "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1")

    def test_builds_weapon_url_parts(self):
        parts = build_task_url_parts(self.weapon_task)
        self.assertEqual(parts["filter_path"], "quality:3/slot:21/type:15")
        self.assertEqual(parts["path"], "items/weapons/quality:3/slot:21/type:15")
        self.assertEqual(parts["query_string"], "")
        self.assertEqual(parts["url"], "https://www.wowhead.com/items/weapons/quality:3/slot:21/type:15")

    def test_builds_single_query_filter_string(self):
        parts = build_task_url_parts(self.single_query_filter_task)
        self.assertEqual(parts["query_string"], "filter=161;1;0")
        self.assertEqual(
            parts["url"],
            "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=161;1;0",
        )

    def test_builds_multiple_query_filter_string_in_stable_order(self):
        parts = build_task_url_parts(self.query_filter_task)
        self.assertEqual(parts["query_string"], "filter=161:195;1:1;0:0")
        self.assertEqual(
            parts["url"],
            "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=161:195;1:1;0:0",
        )

    def test_any_query_filter_value_is_ignored(self):
        parts = build_task_url_parts(self.any_query_filter_task)
        self.assertEqual(parts["query_string"], "filter=195;1;0")
        self.assertEqual(
            parts["url"],
            "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=195;1;0",
        )


if __name__ == "__main__":
    unittest.main()

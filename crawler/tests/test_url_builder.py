import unittest

from core.url_builder import build_task_url_parts


class UrlBuilderTest(unittest.TestCase):
    def setUp(self):
        self.armor_task = {
            "task_id": "uncommon-head-cloth",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
        }
        self.weapon_task = {
            "task_id": "weapon-rare-main_hand_21-daggers_15",
            "quality": "rare",
            "category": "weapon",
            "slot": "main_hand_21",
            "type": "daggers_15",
        }
        self.query_filter_task = {
            "task_id": "uncommon-head-cloth-filtered",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "available_to_players": "yes",
                "can_be_worn_equipped": "yes",
            },
        }
        self.single_query_filter_task = {
            "task_id": "uncommon-head-cloth-player",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "available_to_players": "yes",
            },
        }
        self.any_query_filter_task = {
            "task_id": "uncommon-head-cloth-any",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "available_to_players": "any",
                "can_be_worn_equipped": "yes",
            },
        }
        self.disenchantable_query_filter_task = {
            "task_id": "uncommon-head-cloth-disenchantable-no",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "disenchantable": "no",
            },
        }
        self.combined_query_filter_task = {
            "task_id": "uncommon-head-cloth-combined",
            "quality": "uncommon",
            "category": "armor",
            "slot": "head_1",
            "type": "cloth_armor_1",
            "query_filters": {
                "available_to_players": "yes",
                "disenchantable": "no",
                "can_be_worn_equipped": "yes",
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

    def test_builds_disenchantable_query_filter_string(self):
        parts = build_task_url_parts(self.disenchantable_query_filter_task)
        self.assertEqual(parts["query_string"], "filter=8;2;0")
        self.assertEqual(
            parts["url"],
            "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=8;2;0",
        )

    def test_builds_combined_query_filter_string_in_stable_order(self):
        parts = build_task_url_parts(self.combined_query_filter_task)
        self.assertEqual(parts["query_string"], "filter=161:195:8;1:1:2;0:0:0")
        self.assertEqual(
            parts["url"],
            "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=161:195:8;1:1:2;0:0:0",
        )


if __name__ == "__main__":
    unittest.main()

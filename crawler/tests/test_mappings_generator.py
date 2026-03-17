import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.mappings_generator import (
    build_generated_mappings_data,
    normalize_label_to_key,
    render_mappings_data_module,
    write_mappings_data_module,
)


NORMALIZED_MAPPINGS = {
    "categories": {
        "armor": {"path": "armor"},
        "weapon": {"path": "weapons"},
    },
    "qualities": [
        {"value": 2, "label": "Uncommon"},
        {"value": 3, "label": "Rare"},
        {"value": 4, "label": "Epic"},
    ],
    "slots": [
        {"value": 1, "label": "Head"},
        {"value": 21, "label": "Main Hand"},
        {"value": 23, "label": "Held In Off-hand"},
    ],
    "types": {
        "armor": [
            {"value": 1, "label": "Cloth Armor"},
            {"value": 0, "label": "Miscellaneous (Armor)"},
        ],
        "weapon": [
            {"value": 15, "label": "Daggers"},
            {"value": 10, "label": "Staves"},
            {"value": 14, "label": "Miscellaneous (Weapons)"},
        ],
    },
    "query_filters": [
        {"id": 8, "label": "Disenchantable", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
        {"id": 161, "label": "Available to players", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
        {"id": 195, "label": "Can be worn/equipped", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
    ],
}


class MappingsGeneratorTest(unittest.TestCase):
    def test_normalize_label_to_key_uses_wowhead_label_shape(self):
        self.assertEqual(normalize_label_to_key("Main Hand", 21), "main_hand_21")
        self.assertEqual(normalize_label_to_key("Cloth Armor", 1), "cloth_armor_1")
        self.assertEqual(normalize_label_to_key("Miscellaneous (Weapons)", 14), "miscellaneous_weapons_14")
        self.assertEqual(normalize_label_to_key("Can be worn/equipped", 195), "can_be_worn_equipped_195")
        self.assertEqual(normalize_label_to_key("Held In Off-hand", 23), "held_in_off_hand_23")

    def test_build_generated_mappings_data_uses_semantic_quality_and_filter_keys(self):
        generated = build_generated_mappings_data(NORMALIZED_MAPPINGS)

        self.assertEqual(generated["QUALITIES"]["uncommon"]["wowhead"], {"facet": "quality", "value": 2})
        self.assertEqual(generated["SLOTS"]["main_hand_21"]["wowhead"], {"facet": "slot", "value": 21})
        self.assertEqual(generated["SLOTS"]["held_in_off_hand_23"]["wowhead"], {"facet": "slot", "value": 23})
        self.assertEqual(generated["CATEGORY_TYPES"]["armor"]["cloth_armor_1"]["wowhead"], {"facet": "type", "value": 1})
        self.assertEqual(generated["CATEGORY_TYPES"]["weapon"]["daggers_15"]["wowhead"], {"facet": "type", "value": 15})
        self.assertEqual(generated["QUERY_FILTERS"]["can_be_worn_equipped"]["wowhead"], {"id": 195})

    def test_render_mappings_data_module_contains_generated_keys_and_values(self):
        module_text = render_mappings_data_module(NORMALIZED_MAPPINGS)

        self.assertIn('"uncommon"', module_text)
        self.assertIn('"main_hand_21"', module_text)
        self.assertIn('"cloth_armor_1"', module_text)
        self.assertIn('"daggers_15"', module_text)
        self.assertIn('"can_be_worn_equipped"', module_text)
        self.assertIn('"available_to_players"', module_text)
        self.assertIn('QUERY_FILTER_ORDER = ("available_to_players", "can_be_worn_equipped", "disenchantable")', module_text)
        self.assertNotIn("def normalize_task", module_text)
        self.assertNotIn("def validate_task", module_text)

    def test_write_mappings_data_module_writes_python_file(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "mappings_data.py"
            written_path = write_mappings_data_module(output_path, NORMALIZED_MAPPINGS)

            self.assertEqual(written_path, output_path)
            module_text = output_path.read_text(encoding="utf-8")
            self.assertIn('QUALITIES = {', module_text)
            self.assertIn('SLOTS = {', module_text)
            self.assertIn('CATEGORY_TYPES = {', module_text)
            self.assertIn('QUERY_FILTERS = {', module_text)


if __name__ == "__main__":
    unittest.main()

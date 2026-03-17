import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.normalized_mappings import (
    build_normalized_mappings,
    extract_query_filters,
    extract_select_options,
    write_normalized_mappings,
)


ARMOR_HTML = """
<select id="filter-facet-quality">
  <option value="0">Poor</option>
  <option value="2">Uncommon</option>
  <option value="3">Rare</option>
  <option value="4">Epic</option>
</select>
<select id="filter-facet-slot">
  <option value="1">Head</option>
  <option value="16">Back</option>
</select>
<select id="filter-facet-type">
  <option value="1">Cloth Armor</option>
  <option value="6">Shields</option>
</select>
"""

WEAPONS_HTML = """
<select id="filter-facet-quality">
  <option value="0">Poor</option>
  <option value="2">Uncommon</option>
  <option value="3">Rare</option>
  <option value="4">Epic</option>
</select>
<select id="filter-facet-slot">
  <option value="21">Main Hand</option>
  <option value="17">Two-Hand</option>
</select>
<select id="filter-facet-type">
  <option value="15">Daggers</option>
  <option value="10">Staves</option>
</select>
"""

FILTER_INIT_DATA = {
    "filters": [
        {"heading": True, "name": "General"},
        {"id": 8, "name": "Disenchantable", "options": [[1, "Yes"], [2, "No"]]},
        {"id": 161, "name": "Available to players", "options": [[1, "Yes"], [2, "No"]]},
        {"id": 195, "name": "Can be worn/equipped", "options": [[1, "Yes"], [2, "No"]]},
    ]
}


class NormalizedMappingsTest(unittest.TestCase):
    def test_extract_select_options_reads_value_and_label(self):
        self.assertEqual(
            extract_select_options(WEAPONS_HTML, "filter-facet-slot"),
            [
                {"value": 21, "label": "Main Hand"},
                {"value": 17, "label": "Two-Hand"},
            ],
        )

    def test_extract_query_filters_keeps_target_filters_only(self):
        self.assertEqual(
            extract_query_filters(FILTER_INIT_DATA),
            [
                {
                    "id": 8,
                    "label": "Disenchantable",
                    "values": [
                        {"value": 1, "label": "Yes"},
                        {"value": 2, "label": "No"},
                    ],
                },
                {
                    "id": 161,
                    "label": "Available to players",
                    "values": [
                        {"value": 1, "label": "Yes"},
                        {"value": 2, "label": "No"},
                    ],
                },
                {
                    "id": 195,
                    "label": "Can be worn/equipped",
                    "values": [
                        {"value": 1, "label": "Yes"},
                        {"value": 2, "label": "No"},
                    ],
                },
            ],
        )

    def test_build_normalized_mappings_combines_html_and_filter_json(self):
        mappings = build_normalized_mappings(
            armor_html=ARMOR_HTML,
            armor_filters=FILTER_INIT_DATA,
            weapons_html=WEAPONS_HTML,
            weapons_filters=FILTER_INIT_DATA,
        )

        self.assertEqual(
            mappings,
            {
                "categories": {
                    "armor": {"path": "armor"},
                    "weapon": {"path": "weapons"},
                },
                "qualities": [
                    {"value": 2, "label": "Uncommon"},
                    {"value": 3, "label": "Rare"},
                    {"value": 4, "label": "Epic"},
                ],
                "slots": {
                    "armor": [
                        {"value": 1, "label": "Head"},
                        {"value": 16, "label": "Back"},
                    ],
                    "weapon": [
                        {"value": 17, "label": "Two-Hand"},
                        {"value": 21, "label": "Main Hand"},
                    ],
                },
                "types": {
                    "armor": [
                        {"value": 1, "label": "Cloth Armor"},
                        {"value": 6, "label": "Shields"},
                    ],
                    "weapon": [
                        {"value": 10, "label": "Staves"},
                        {"value": 15, "label": "Daggers"},
                    ],
                },
                "query_filters": [
                    {
                        "id": 8,
                        "label": "Disenchantable",
                        "values": [
                            {"value": 1, "label": "Yes"},
                            {"value": 2, "label": "No"},
                        ],
                    },
                    {
                        "id": 161,
                        "label": "Available to players",
                        "values": [
                            {"value": 1, "label": "Yes"},
                            {"value": 2, "label": "No"},
                        ],
                    },
                    {
                        "id": 195,
                        "label": "Can be worn/equipped",
                        "values": [
                            {"value": 1, "label": "Yes"},
                            {"value": 2, "label": "No"},
                        ],
                    },
                ],
            },
        )

    def test_build_normalized_mappings_rejects_inconsistent_query_filters(self):
        mismatched_filters = {
            "filters": [
                {"id": 8, "name": "Disenchantable", "options": [[1, "Yes"], [2, "No"]]},
                {"id": 161, "name": "Available to players", "options": [[1, "Yes"], [2, "No"]]},
                {"id": 195, "name": "Can Equip", "options": [[1, "Yes"], [2, "No"]]},
            ]
        }

        with self.assertRaises(ValueError):
            build_normalized_mappings(
                armor_html=ARMOR_HTML,
                armor_filters=FILTER_INIT_DATA,
                weapons_html=WEAPONS_HTML,
                weapons_filters=mismatched_filters,
            )

    def test_write_normalized_mappings_writes_json_file(self):
        mappings = build_normalized_mappings(
            armor_html=ARMOR_HTML,
            armor_filters=FILTER_INIT_DATA,
            weapons_html=WEAPONS_HTML,
            weapons_filters=FILTER_INIT_DATA,
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "normalized_mappings.json"
            written_path = write_normalized_mappings(output_path, mappings)

            self.assertEqual(written_path, output_path)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                mappings,
            )


if __name__ == "__main__":
    unittest.main()

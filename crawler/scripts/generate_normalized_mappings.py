import json
import sys
from pathlib import Path

from core.normalized_mappings import build_normalized_mappings, write_normalized_mappings


DEFAULT_OUTPUT_PATH = Path("outputs/filter_pages/normalized_mappings.json")


def run(argv=None):
    """从本地 armor/weapons HTML 与 filters.json 生成 normalized mappings。"""
    argv = list(argv or [])
    if len(argv) not in (0, 4, 5):
        raise SystemExit(
            "Usage: python3 -m scripts.generate_normalized_mappings "
            "[armor_html armor_filters weapons_html weapons_filters [output_path]]"
        )

    if len(argv) == 0:
        armor_html_path = Path("outputs/filter_pages/armor.html")
        armor_filters_path = Path("outputs/filter_pages/armor.filters.json")
        weapons_html_path = Path("outputs/filter_pages/weapons.html")
        weapons_filters_path = Path("outputs/filter_pages/weapons.filters.json")
        output_path = DEFAULT_OUTPUT_PATH
    else:
        armor_html_path = Path(argv[0])
        armor_filters_path = Path(argv[1])
        weapons_html_path = Path(argv[2])
        weapons_filters_path = Path(argv[3])
        output_path = Path(argv[4]) if len(argv) == 5 else DEFAULT_OUTPUT_PATH

    mappings = build_normalized_mappings(
        armor_html=armor_html_path.read_text(encoding="utf-8"),
        armor_filters=json.loads(armor_filters_path.read_text(encoding="utf-8")),
        weapons_html=weapons_html_path.read_text(encoding="utf-8"),
        weapons_filters=json.loads(weapons_filters_path.read_text(encoding="utf-8")),
    )
    return write_normalized_mappings(output_path, mappings)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

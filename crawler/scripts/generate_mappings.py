import json
import sys
from pathlib import Path

from core.mappings_generator import write_mappings_module


DEFAULT_NORMALIZED_PATH = Path("outputs/filter_pages/normalized_mappings.json")
DEFAULT_OUTPUT_PATH = Path("core/mappings.py")


def run(argv=None):
    """从 normalized_mappings.json 生成 crawler mappings 模块。"""
    argv = list(argv or [])
    if len(argv) not in (0, 1, 2):
        raise SystemExit(
            "Usage: python3 -m scripts.generate_mappings [normalized_mappings_path] [output_path]"
        )

    normalized_path = Path(argv[0]) if len(argv) >= 1 else DEFAULT_NORMALIZED_PATH
    output_path = Path(argv[1]) if len(argv) == 2 else DEFAULT_OUTPUT_PATH
    normalized_data = json.loads(normalized_path.read_text(encoding="utf-8"))
    return write_mappings_module(output_path, normalized_data)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

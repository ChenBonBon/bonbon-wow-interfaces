import sys
from pathlib import Path

from core.lua_exporter import write_lua_item_id_table


def run(argv=None):
    """执行 Lua 数据导出的薄脚本入口。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: python3 -m scripts.export_lua <items_unique_path> [output_path]")

    items_unique_path = Path(argv[0])
    output_path = Path(argv[1]) if len(argv) == 2 else None
    return write_lua_item_id_table(items_unique_path, output_path=output_path)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

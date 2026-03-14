import sys
from pathlib import Path

from core.aggregator import write_unique_items


def run(argv=None):
    """执行单次运行汇总的薄脚本入口。"""
    argv = list(argv or [])
    if len(argv) != 1:
        raise SystemExit("Usage: python3 -m scripts.aggregate_run <manifest_path>")

    manifest_path = Path(argv[0])
    return write_unique_items(manifest_path)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

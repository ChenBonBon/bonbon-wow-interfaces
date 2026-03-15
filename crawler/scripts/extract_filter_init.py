import sys
from pathlib import Path

from core.filter_init import build_filter_json_output_path, write_filter_init_json


def run(argv=None):
    """从本地 HTML 中提取 Filter.init 并导出 JSON。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: python3 -m scripts.extract_filter_init <html_path> [output_path]")

    html_path = Path(argv[0])
    output_path = Path(argv[1]) if len(argv) == 2 else build_filter_json_output_path(html_path)
    return write_filter_init_json(html_path, output_path=output_path)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

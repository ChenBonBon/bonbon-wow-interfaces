import sys
from pathlib import Path

from core.filter_init import build_filter_page_output_path, write_filter_page_html


def run(argv=None, fetch_url=None):
    """抓取 Wowhead 页面并把 HTML 保存到本地。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: python3 -m scripts.fetch_filter_page <url> [output_path]")

    url = argv[0]
    output_path = Path(argv[1]) if len(argv) == 2 else build_filter_page_output_path("filter-page")
    return write_filter_page_html(url, output_path=output_path, fetch_url=fetch_url)


def main():
    """命令行入口。"""
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == "__main__":
    main()

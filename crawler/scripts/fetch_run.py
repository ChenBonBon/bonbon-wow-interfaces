import sys
from pathlib import Path

from core.fetcher import fetch_manifest_results


def run(argv=None, fetch_url=None):
    """执行单次运行抓取的薄脚本入口。"""
    argv = list(argv or [])
    if len(argv) != 1:
        raise SystemExit("Usage: python3 -m scripts.fetch_run <manifest_path>")

    manifest_path = Path(argv[0])
    fetch_manifest_results(manifest_path, fetch_url=fetch_url)
    return manifest_path


def main():
    """命令行入口。"""
    manifest_path = run(sys.argv[1:])
    print(manifest_path)


if __name__ == "__main__":
    main()

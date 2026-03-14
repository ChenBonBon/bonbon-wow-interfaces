import sys
from pathlib import Path

from core.fetcher import retry_failed_manifest_results
from scripts.aggregate_run import run as run_aggregate
from scripts.export_lua import run as run_export_lua


def run(argv=None, fetch_url=None, export_output_path=None):
    """执行失败任务重跑后继续聚合和导出的薄脚本入口。"""
    argv = list(argv or [])
    if len(argv) != 1:
        raise SystemExit("Usage: python3 -m scripts.retry_failed_run <manifest_path>")

    manifest_path = Path(argv[0])
    retry_failed_manifest_results(manifest_path, fetch_url=fetch_url)
    run_aggregate([str(manifest_path)])
    export_args = [str(manifest_path)]
    if export_output_path is not None:
        export_args.append(str(export_output_path))
    run_export_lua(export_args)
    return manifest_path


def main():
    """命令行入口。"""
    manifest_path = run(sys.argv[1:])
    print(manifest_path)


if __name__ == "__main__":
    main()

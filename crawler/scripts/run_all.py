import sys
from pathlib import Path

from scripts.aggregate_run import run as run_aggregate
from scripts.export_lua import run as run_export_lua
from scripts.fetch_run import run as run_fetch
from scripts.generate_run import run as run_generate


def run(argv=None, fetch_url=None, export_output_path=None):
    """执行 generate -> fetch -> aggregate -> export 的总入口。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: python3 -m scripts.run_all <task_file> [outputs_dir]")

    manifest_path = run_generate(argv)
    run_fetch([str(manifest_path)], fetch_url=fetch_url)
    run_aggregate([str(manifest_path)])
    export_args = [str(manifest_path)]
    if export_output_path is not None:
        export_args.append(str(export_output_path))
    run_export_lua(export_args)
    return Path(manifest_path)


def main():
    """命令行入口。"""
    manifest_path = run(sys.argv[1:])
    print(manifest_path)


if __name__ == "__main__":
    main()

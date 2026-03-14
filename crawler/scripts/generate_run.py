import sys
from pathlib import Path

from core.runner import write_run_manifest


def run(argv=None):
    """生成单次运行 manifest 的薄脚本入口。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: python3 -m scripts.generate_run <task_file> [outputs_dir]")

    task_file = Path(argv[0])
    outputs_dir = Path(argv[1]) if len(argv) == 2 else None
    return write_run_manifest(task_file, outputs_dir=outputs_dir)


def main():
    """命令行入口。"""
    manifest_path = run(sys.argv[1:])
    print(manifest_path)


if __name__ == "__main__":
    main()

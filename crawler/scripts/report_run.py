import sys
from pathlib import Path

from core.run_report import write_run_report


DEFAULT_OUTPUT_FILE_NAME = 'run-report.json'


def run(argv=None):
    """根据 manifest 生成单次运行统计文件。"""
    argv = list(argv or [])
    if len(argv) not in (1, 2):
        raise SystemExit('Usage: python3 -m scripts.report_run <manifest_path> [output_path]')

    manifest_path = Path(argv[0])
    output_path = Path(argv[1]) if len(argv) == 2 else manifest_path.parent / DEFAULT_OUTPUT_FILE_NAME
    return write_run_report(manifest_path, output_path=output_path)



def main():
    output_path = run(sys.argv[1:])
    print(output_path)


if __name__ == '__main__':
    main()

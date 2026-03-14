import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from core.mappings import normalize_task, validate_task
from core.url_builder import build_task_url_parts


def load_tasks(task_file_path):
    """读取任务配置文件。"""
    task_file = Path(task_file_path)
    return json.loads(task_file.read_text(encoding="utf-8"))


def build_run_manifest(task_file_path, generated_at=None):
    """生成单次运行的任务清单，不写文件。"""
    generated_at = _normalize_generated_at(generated_at)
    run_id = generated_at.strftime("%Y-%m-%dT%H-%M-%S")

    tasks = []
    for task in load_tasks(task_file_path):
        normalized = normalize_task(task)
        if not normalized["enabled"]:
            continue

        validate_task(normalized)
        planned_task = dict(normalized)
        planned_task["status"] = "planned"
        planned_task.update(build_task_url_parts(normalized))
        tasks.append(planned_task)

    return {
        "run_id": run_id,
        "generated_at": generated_at.isoformat(),
        "task_file": str(Path(task_file_path)),
        "task_count": len(tasks),
        "tasks": tasks,
    }


def write_run_manifest(task_file_path, outputs_dir=None, generated_at=None):
    """创建运行目录并写出 manifest.json。"""
    manifest = build_run_manifest(task_file_path, generated_at=generated_at)
    outputs_dir = Path(outputs_dir) if outputs_dir is not None else Path(__file__).resolve().parents[1] / "outputs"
    run_dir = outputs_dir / manifest["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest_path


def main(argv=None):
    """解析命令行参数并生成单次运行清单。"""
    parser = argparse.ArgumentParser(description="生成 Wowhead 任务运行清单")
    parser.add_argument("--task-file", required=True, help="任务配置文件路径")
    args = parser.parse_args(argv)

    manifest_path = write_run_manifest(args.task_file)
    print(manifest_path)


def _normalize_generated_at(generated_at):
    """标准化生成时间，默认使用 UTC 当前时间。"""
    if generated_at is None:
        return datetime.now(timezone.utc)
    return generated_at


if __name__ == "__main__":
    main()

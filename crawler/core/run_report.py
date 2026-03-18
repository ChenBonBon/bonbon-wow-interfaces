import json
from pathlib import Path

from core.aggregator import read_items_by_task


DEFAULT_REPORT_FILE_NAME = 'run-report.json'
ITEMS_UNIQUE_FILE_NAME = 'items.unique.json'


def build_run_report(manifest_path, extra_fields=None):
    """从 manifest 与任务结果文件构建单次运行统计。"""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    run_dir = manifest_file.parent
    items_by_task = read_items_by_task(manifest_file)

    tasks = manifest.get('tasks', [])
    fetched_task_ids = []
    failed_task_ids = []
    failed_tasks = []
    planned_task_ids = []
    empty_result_task_ids = []

    for task in tasks:
        task_id = task['task_id']
        status = task.get('status')
        if status == 'fetched':
            fetched_task_ids.append(task_id)
            task_result = items_by_task.get(task_id, {'items': []})
            if len(task_result.get('items', [])) == 0:
                empty_result_task_ids.append(task_id)
        elif status == 'failed':
            failed_task_ids.append(task_id)
            failed_tasks.append(
                {
                    'task_id': task_id,
                    'error_message': task.get('error_message', ''),
                }
            )
        elif status == 'planned':
            planned_task_ids.append(task_id)

    items_unique_path = run_dir / ITEMS_UNIQUE_FILE_NAME
    unique_items = json.loads(items_unique_path.read_text(encoding='utf-8')) if items_unique_path.exists() else []

    report = {
        'run_id': manifest.get('run_id'),
        'task_count': len(tasks),
        'fetched_count': len(fetched_task_ids),
        'failed_count': len(failed_task_ids),
        'planned_count': len(planned_task_ids),
        'unique_item_count': len(unique_items),
        'failed_task_ids': failed_task_ids,
        'failed_tasks': failed_tasks,
        'empty_result_task_ids': empty_result_task_ids,
    }
    if extra_fields:
        report.update(extra_fields)
    return report


def write_run_report(manifest_path, output_path=None, extra_fields=None):
    """写出单次运行统计 JSON。"""
    manifest_file = Path(manifest_path)
    output_file = Path(output_path) if output_path is not None else manifest_file.parent / DEFAULT_REPORT_FILE_NAME
    report = build_run_report(manifest_file, extra_fields=extra_fields)
    output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return output_file

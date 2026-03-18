import json
from pathlib import Path


ITEMS_BY_TASK_FILE_NAME = "items.by-task.json"


def read_items_by_task(manifest_path):
    """读取单次运行的按任务聚合结果文件。"""
    manifest_file = Path(manifest_path)
    results_path = manifest_file.parent / ITEMS_BY_TASK_FILE_NAME
    if not results_path.exists():
        return {}
    return json.loads(results_path.read_text(encoding="utf-8"))


def build_unique_items(manifest_path):
    """从单次运行结果中构建唯一物品列表。"""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    items_by_task = read_items_by_task(manifest_file)

    unique_items = []
    seen_item_ids = set()

    for task in manifest["tasks"]:
        if task.get("status") != "fetched":
            continue

        task_result = items_by_task.get(task["task_id"], {"items": []})
        for item in task_result.get("items", []):
            item_id = item["itemId"]
            if item_id in seen_item_ids:
                continue

            seen_item_ids.add(item_id)
            unique_items.append(
                {
                    "itemId": item_id,
                    "name": item["name"],
                }
            )

    return unique_items


def write_unique_items(manifest_path):
    """写出唯一物品列表到 items.unique.json。"""
    manifest_file = Path(manifest_path)
    output_path = manifest_file.parent / "items.unique.json"
    output_path.write_text(
        json.dumps(build_unique_items(manifest_file), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path

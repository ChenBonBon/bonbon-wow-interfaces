import json
from pathlib import Path


def build_unique_items(manifest_path):
    """从单次运行结果中构建唯一物品列表。"""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    output_dir = manifest_file.parent

    unique_items = []
    seen_item_ids = set()

    for task in manifest["tasks"]:
        if task.get("status") != "fetched":
            continue

        task_result_path = output_dir / f"{task['task_id']}.json"
        task_result = json.loads(task_result_path.read_text(encoding="utf-8"))
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

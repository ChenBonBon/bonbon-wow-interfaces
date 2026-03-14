import json
from pathlib import Path


DEFAULT_LUA_OUTPUT_PATH = Path(__file__).resolve().parents[2] / "QuickDisenchant" / "DisenchantableByWowhead.lua"
ITEMS_UNIQUE_FILE_NAME = "items.unique.json"


def render_lua_item_id_table(items):
    """把唯一物品列表渲染为 Lua itemId 布尔表。"""
    sorted_ids = sorted(item["itemId"] for item in items)
    lines = [
        "QD = QD or _G.QuickDisenchantNS",
        "QD.WOWHEAD_DISENCHANTABLE_ITEM_IDS = {",
    ]

    for item_id in sorted_ids:
        lines.append(f"  [{item_id}] = true,")

    lines.append("}")
    return "\n".join(lines) + "\n"


def resolve_items_unique_path(manifest_path):
    """根据 manifest.json 定位同目录下的唯一物品汇总文件。"""
    manifest_file = Path(manifest_path)
    return manifest_file.parent / ITEMS_UNIQUE_FILE_NAME


def validate_manifest_for_export(manifest):
    """确认 manifest 中所有任务都已成功抓取。"""
    incomplete_statuses = sorted(
        {
            task.get("status", "missing")
            for task in manifest.get("tasks", [])
            if task.get("status") != "fetched"
        }
    )

    if incomplete_statuses:
        raise ValueError(
            "Cannot export Lua data because manifest still contains incomplete tasks: "
            + ", ".join(incomplete_statuses)
        )


def write_lua_item_id_table(manifest_path, output_path=None):
    """读取 manifest.json 并在全部任务成功后写出 Lua 数据文件。"""
    manifest_file = Path(manifest_path)
    output_file = Path(output_path) if output_path is not None else DEFAULT_LUA_OUTPUT_PATH
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    validate_manifest_for_export(manifest)

    items_unique_file = resolve_items_unique_path(manifest_file)
    items = json.loads(items_unique_file.read_text(encoding="utf-8"))

    output_file.write_text(
        render_lua_item_id_table(items),
        encoding="utf-8",
    )
    return output_file

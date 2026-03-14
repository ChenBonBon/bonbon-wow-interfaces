import json
from pathlib import Path


DEFAULT_LUA_OUTPUT_PATH = Path(__file__).resolve().parents[2] / "QuickDisenchant" / "DisenchantableByWowhead.lua"


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


def write_lua_item_id_table(items_unique_path, output_path=None):
    """读取 items.unique.json 并写出 Lua 数据文件。"""
    items_unique_file = Path(items_unique_path)
    output_file = Path(output_path) if output_path is not None else DEFAULT_LUA_OUTPUT_PATH
    items = json.loads(items_unique_file.read_text(encoding="utf-8"))

    output_file.write_text(
        render_lua_item_id_table(items),
        encoding="utf-8",
    )
    return output_file

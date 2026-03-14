from core.mappings import CATEGORIES, CATEGORY_TYPES, QUALITIES, SLOTS, normalize_task, validate_task


WOWHEAD_BASE_URL = "https://www.wowhead.com"


def build_task_url_parts(task):
    """将语义化任务转换为 Wowhead URL 相关字段。"""
    normalized = normalize_task(task)
    validate_task(normalized)

    category_key = normalized["category"]
    quality_key = normalized["quality"]
    slot_key = normalized["slot"]
    type_key = normalized["type"]

    category_path = CATEGORIES[category_key]["wowhead"]["path"]
    filter_path = "/".join(
        (
            _build_filter_segment(QUALITIES[quality_key]["wowhead"]),
            _build_filter_segment(SLOTS[slot_key]["wowhead"]),
            _build_filter_segment(CATEGORY_TYPES[category_key][type_key]["wowhead"]),
        )
    )
    path = f"items/{category_path}/{filter_path}"

    return {
        "url": f"{WOWHEAD_BASE_URL}/{path}",
        "path": path,
        "filter_path": filter_path,
    }


def _build_filter_segment(metadata):
    """把单个筛选元数据拼成 facet:value 片段。"""
    return f"{metadata['facet']}:{metadata['value']}"

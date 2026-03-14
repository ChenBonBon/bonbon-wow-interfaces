from core.mappings import (
    CATEGORIES,
    CATEGORY_TYPES,
    QUALITIES,
    QUERY_FILTERS,
    QUERY_FILTER_ORDER,
    SLOTS,
    normalize_task,
    validate_task,
)


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
    query_string = _build_query_string(normalized["query_filters"])
    url = f"{WOWHEAD_BASE_URL}/{path}"
    if query_string != "":
        url = f"{url}?{query_string}"

    return {
        "url": url,
        "path": path,
        "filter_path": filter_path,
        "query_string": query_string,
    }


def _build_filter_segment(metadata):
    """把单个筛选元数据拼成 facet:value 片段。"""
    return f"{metadata['facet']}:{metadata['value']}"


def _build_query_string(query_filters):
    """把语义化查询筛选转换为 Wowhead filter 参数。"""
    filter_ids = []
    filter_values = []

    for filter_name in QUERY_FILTER_ORDER:
        selected_value = query_filters.get(filter_name, "any")
        value_id = QUERY_FILTERS[filter_name]["values"][selected_value]
        if value_id is None:
            continue

        filter_ids.append(str(QUERY_FILTERS[filter_name]["wowhead"]["id"]))
        filter_values.append(str(value_id))

    if len(filter_ids) == 0:
        return ""

    zero_values = ":".join("0" for _ in filter_ids)
    return f"filter={':'.join(filter_ids)};{':'.join(filter_values)};{zero_values}"

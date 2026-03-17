from copy import deepcopy

from core.mappings_data import (
    CATEGORIES,
    CATEGORY_SLOTS,
    CATEGORY_TYPES,
    QUALITIES,
    QUERY_FILTERS,
    QUERY_FILTER_ORDER,
)


REQUIRED_TASK_FIELDS = ("task_id", "quality", "category", "slot", "type")


def get_category_type_meta(category, type_name):
    category_meta = CATEGORY_TYPES.get(category)
    if category_meta is None:
        raise ValueError(f"未知 category: {category}")

    type_meta = category_meta.get(type_name)
    if type_meta is None:
        raise ValueError(f"未知 type: {category}.{type_name}")

    return deepcopy(type_meta)


def get_category_slot_meta(category, slot_name):
    category_meta = CATEGORY_SLOTS.get(category)
    if category_meta is None:
        raise ValueError(f"未知 category: {category}")

    slot_meta = category_meta.get(slot_name)
    if slot_meta is None:
        raise ValueError(f"未知 slot: {category}.{slot_name}")

    return deepcopy(slot_meta)


def normalize_task(task):
    normalized = deepcopy(task)
    normalized.setdefault("enabled", True)
    normalized.setdefault("query_filters", {})
    return normalized


def validate_task(task):
    normalized = normalize_task(task)

    for field_name in REQUIRED_TASK_FIELDS:
        value = normalized.get(field_name)
        if not isinstance(value, str) or value == "":
            raise ValueError(f"任务字段缺失或非法: {field_name}")

    if not isinstance(normalized["enabled"], bool):
        raise ValueError("任务字段缺失或非法: enabled")

    if not isinstance(normalized["query_filters"], dict):
        raise ValueError("任务字段缺失或非法: query_filters")

    if normalized["quality"] not in QUALITIES:
        raise ValueError(f"未知 quality: {normalized['quality']}")

    if normalized["category"] not in CATEGORIES:
        raise ValueError(f"未知 category: {normalized['category']}")

    get_category_slot_meta(normalized["category"], normalized["slot"])

    get_category_type_meta(normalized["category"], normalized["type"])

    for filter_name, filter_value in normalized["query_filters"].items():
        filter_meta = QUERY_FILTERS.get(filter_name)
        if filter_meta is None:
            raise ValueError(f"未知 query_filter: {filter_name}")

        if filter_value not in filter_meta["values"]:
            raise ValueError(f"未知 query_filter 值: {filter_name}.{filter_value}")


def build_task_slug(task):
    normalized = normalize_task(task)
    validate_task(normalized)
    return "-".join((normalized["quality"], normalized["slot"], normalized["type"]))


def describe_task(task):
    normalized = normalize_task(task)
    validate_task(normalized)

    return " ".join(
        (
            QUALITIES[normalized["quality"]]["label"],
            CATEGORY_SLOTS[normalized["category"]][normalized["slot"]]["label"],
            CATEGORY_TYPES[normalized["category"]][normalized["type"]]["label"],
        )
    )

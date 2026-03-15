import json
import re
from pathlib import Path


QUALITY_LABEL_TRANSLATIONS = {
    "Uncommon": "绿色",
    "Rare": "蓝色",
    "Epic": "紫色",
}

DISPLAY_LABEL_TRANSLATIONS = {
    "Head": "头部",
    "Neck": "项链",
    "Shoulder": "肩部",
    "Shirt": "衬衣",
    "Chest": "胸部",
    "Waist": "腰部",
    "Legs": "腿部",
    "Feet": "脚部",
    "Wrist": "手腕",
    "Hands": "手部",
    "Finger": "戒指",
    "Trinket": "饰品",
    "One-Hand": "单手",
    "Shield": "盾牌",
    "Ranged": "远程",
    "Back": "披风",
    "Two-Hand": "双手",
    "Tabard": "战袍",
    "Main Hand": "主手",
    "Off Hand": "副手",
    "Held In Off-hand": "持于副手",
    "Shirts": "衬衣",
    "Tabards": "战袍",
    "Cloaks": "披风",
    "Off-hand Frills": "副手物品",
    "Amulets": "项链",
    "Rings": "戒指",
    "Miscellaneous (Armor)": "其他护甲",
    "Cloth Armor": "布甲",
    "Leather Armor": "皮甲",
    "Mail Armor": "锁甲",
    "Plate Armor": "板甲",
    "Cosmetic": "幻化外观",
    "Shields": "盾牌",
    "Librams": "圣契",
    "Idols": "神像",
    "Totems": "图腾",
    "Sigils": "魔印",
    "Relics": "圣物",
    "One-Handed Axes": "单手斧",
    "Two-Handed Axes": "双手斧",
    "Bows": "弓",
    "Guns": "枪械",
    "One-Handed Maces": "单手锤",
    "Two-Handed Maces": "双手锤",
    "Polearms": "长柄武器",
    "One-Handed Swords": "单手剑",
    "Two-Handed Swords": "双手剑",
    "Warglaives": "战刃",
    "Staves": "法杖",
    "Fist Weapons": "拳套",
    "Miscellaneous (Weapons)": "其他武器",
    "Daggers": "匕首",
    "Thrown": "投掷武器",
    "Crossbows": "弩",
    "Wands": "魔杖",
    "Fishing Poles": "鱼竿",
    "Disenchantable": "可分解",
    "Available to players": "玩家可用",
    "Can be worn/equipped": "可穿戴/可装备",
}

CATEGORIES = {
    "weapon": {"label": "武器", "wowhead": {"path": "weapons"}},
    "armor": {"label": "护甲", "wowhead": {"path": "armor"}},
}

DEFAULT_QUERY_FILTER_ORDER = (
    ("Available to players", 161),
    ("Can be worn/equipped", 195),
    ("Disenchantable", 8),
)


def normalize_label_to_key(label, value):
    text = label.strip().lower()
    text = re.sub(r"[()]+", " ", text)
    text = re.sub(r"[/,]", " ", text)
    text = text.replace("-", " ")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return f"{text.strip('_')}_{value}"


def _display_label(label, fallback=None):
    return DISPLAY_LABEL_TRANSLATIONS.get(label, fallback or label)


def build_generated_mappings_data(normalized_data):
    qualities = {}
    for item in normalized_data["qualities"]:
        key = normalize_label_to_key(item["label"], item["value"])
        qualities[key] = {
            "label": QUALITY_LABEL_TRANSLATIONS.get(item["label"], item["label"]),
            "wowhead": {"facet": "quality", "value": item["value"]},
        }

    slots = {}
    for item in normalized_data["slots"]:
        key = normalize_label_to_key(item["label"], item["value"])
        slots[key] = {
            "label": _display_label(item["label"]),
            "wowhead": {"facet": "slot", "value": item["value"]},
        }

    category_types = {}
    for category_key, items in normalized_data["types"].items():
        category_types[category_key] = {}
        for item in items:
            key = normalize_label_to_key(item["label"], item["value"])
            category_types[category_key][key] = {
                "label": _display_label(item["label"]),
                "wowhead": {"facet": "type", "value": item["value"]},
            }

    query_filters = {}
    for item in normalized_data["query_filters"]:
        key = normalize_label_to_key(item["label"], item["id"])
        query_filters[key] = {
            "label": _display_label(item["label"]),
            "wowhead": {"id": item["id"]},
            "values": {
                "yes": next((value["value"] for value in item["values"] if value["label"] == "Yes"), 1),
                "no": next((value["value"] for value in item["values"] if value["label"] == "No"), 2),
                "any": None,
            },
        }

    query_filter_order = tuple(
        normalize_label_to_key(label, value)
        for label, value in DEFAULT_QUERY_FILTER_ORDER
        if normalize_label_to_key(label, value) in query_filters
    ) + tuple(
        key
        for key in sorted(query_filters)
        if key not in {normalize_label_to_key(label, value) for label, value in DEFAULT_QUERY_FILTER_ORDER}
    )

    return {
        "QUALITIES": qualities,
        "CATEGORIES": CATEGORIES,
        "SLOTS": slots,
        "CATEGORY_TYPES": category_types,
        "QUERY_FILTERS": query_filters,
        "QUERY_FILTER_ORDER": query_filter_order,
    }


def _render_assignment(name, value):
    rendered = json.dumps(value, ensure_ascii=False, indent=4)
    rendered = rendered.replace(": null", ": None")
    rendered = rendered.replace(": true", ": True")
    rendered = rendered.replace(": false", ": False")
    return f"{name} = " + rendered + "\n"


def _render_tuple(value):
    items = ", ".join(json.dumps(item, ensure_ascii=False) for item in value)
    if len(value) == 1:
        items += ","
    return f"({items})"


def render_mappings_data_module(normalized_data):
    generated = build_generated_mappings_data(normalized_data)
    sections = [
        _render_assignment("QUALITIES", generated["QUALITIES"]),
        "\n",
        _render_assignment("CATEGORIES", generated["CATEGORIES"]),
        "\n",
        _render_assignment("SLOTS", generated["SLOTS"]),
        "\n",
        _render_assignment("CATEGORY_TYPES", generated["CATEGORY_TYPES"]),
        "\n",
        _render_assignment("QUERY_FILTERS", generated["QUERY_FILTERS"]),
        "\n",
        "QUERY_FILTER_ORDER = " + _render_tuple(generated["QUERY_FILTER_ORDER"]) + "\n",
    ]
    return "".join(sections)


def write_mappings_data_module(output_path, normalized_data):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_mappings_data_module(normalized_data), encoding="utf-8")
    return output_path

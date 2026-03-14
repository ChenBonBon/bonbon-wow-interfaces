from copy import deepcopy


QUALITIES = {
    "uncommon": {"label": "绿色", "wowhead": {"facet": "quality", "value": 2}},
    "rare": {"label": "蓝色", "wowhead": {"facet": "quality", "value": 3}},
    "epic": {"label": "紫色", "wowhead": {"facet": "quality", "value": 4}},
}

CATEGORIES = {
    "weapon": {"label": "武器", "wowhead": {"path": "weapons"}},
    "armor": {"label": "护甲", "wowhead": {"path": "armor"}},
}

SLOTS = {
    "head": {"label": "头部", "wowhead": {"facet": "slot", "value": 1}},
    "neck": {"label": "项链", "wowhead": {"facet": "slot", "value": 2}},
    "shoulder": {"label": "肩部", "wowhead": {"facet": "slot", "value": 3}},
    "cloak": {"label": "披风", "wowhead": {"facet": "slot", "value": 16}},
    "chest": {"label": "胸部", "wowhead": {"facet": "slot", "value": 5}},
    "wrist": {"label": "手腕", "wowhead": {"facet": "slot", "value": 9}},
    "hands": {"label": "手部", "wowhead": {"facet": "slot", "value": 10}},
    "waist": {"label": "腰部", "wowhead": {"facet": "slot", "value": 6}},
    "legs": {"label": "腿部", "wowhead": {"facet": "slot", "value": 7}},
    "feet": {"label": "脚部", "wowhead": {"facet": "slot", "value": 8}},
    "finger": {"label": "戒指", "wowhead": {"facet": "slot", "value": 11}},
    "trinket": {"label": "饰品", "wowhead": {"facet": "slot", "value": 12}},
    "main_hand": {"label": "主手", "wowhead": {"facet": "slot", "value": 21}},
    "off_hand": {"label": "副手", "wowhead": {"facet": "slot", "value": 22}},
    "two_hand": {"label": "双手", "wowhead": {"facet": "slot", "value": 17}},
    "ranged": {"label": "远程", "wowhead": {"facet": "slot", "value": 15}},
}

CATEGORY_TYPES = {
    "weapon": {
        "dagger": {"label": "匕首", "wowhead": {"facet": "type", "value": 15}},
        "fist_weapon": {"label": "拳套", "wowhead": {"facet": "type", "value": 13}},
        "one_handed_axe": {"label": "单手斧", "wowhead": {"facet": "type", "value": 0}},
        "one_handed_mace": {"label": "单手锤", "wowhead": {"facet": "type", "value": 4}},
        "one_handed_sword": {"label": "单手剑", "wowhead": {"facet": "type", "value": 7}},
        "warglaive": {"label": "战刃", "wowhead": {"facet": "type", "value": 9}},
        "polearm": {"label": "长柄武器", "wowhead": {"facet": "type", "value": 6}},
        "staff": {"label": "法杖", "wowhead": {"facet": "type", "value": 10}},
        "two_handed_axe": {"label": "双手斧", "wowhead": {"facet": "type", "value": 1}},
        "two_handed_mace": {"label": "双手锤", "wowhead": {"facet": "type", "value": 5}},
        "two_handed_sword": {"label": "双手剑", "wowhead": {"facet": "type", "value": 8}},
        "bow": {"label": "弓", "wowhead": {"facet": "type", "value": 2}},
        "crossbow": {"label": "弩", "wowhead": {"facet": "type", "value": 18}},
        "gun": {"label": "枪械", "wowhead": {"facet": "type", "value": 3}},
        "wand": {"label": "魔杖", "wowhead": {"facet": "type", "value": 19}},
        "fishing_pole": {"label": "鱼竿", "wowhead": {"facet": "type", "value": 20}},
        "miscellaneous_weapon": {"label": "其他武器", "wowhead": {"facet": "type", "value": 14}},
    },
    "armor": {
        "cloth": {"label": "布甲", "wowhead": {"facet": "type", "value": 1}},
        "leather": {"label": "皮甲", "wowhead": {"facet": "type", "value": 2}},
        "mail": {"label": "锁甲", "wowhead": {"facet": "type", "value": 3}},
        "plate": {"label": "板甲", "wowhead": {"facet": "type", "value": 4}},
        "cosmetic": {"label": "幻化外观", "wowhead": {"facet": "type", "value": 5}},
        "shield": {"label": "盾牌", "wowhead": {"facet": "type", "value": 6}},
        "libram": {"label": "圣契", "wowhead": {"facet": "type", "value": 7}},
        "idol": {"label": "神像", "wowhead": {"facet": "type", "value": 8}},
        "totem": {"label": "图腾", "wowhead": {"facet": "type", "value": 9}},
        "sigil": {"label": "魔印", "wowhead": {"facet": "type", "value": 10}},
        "miscellaneous_armor": {"label": "其他护甲", "wowhead": {"facet": "type", "value": 0}},
    },
}

REQUIRED_TASK_FIELDS = ("task_id", "quality", "category", "slot", "type")


def get_category_type_meta(category, type_name):
    category_meta = CATEGORY_TYPES.get(category)
    if category_meta is None:
        raise ValueError(f"未知 category: {category}")

    type_meta = category_meta.get(type_name)
    if type_meta is None:
        raise ValueError(f"未知 type: {category}.{type_name}")

    return deepcopy(type_meta)


def normalize_task(task):
    normalized = dict(task)
    normalized.setdefault("enabled", True)
    return normalized


def validate_task(task):
    normalized = normalize_task(task)

    for field_name in REQUIRED_TASK_FIELDS:
        value = normalized.get(field_name)
        if not isinstance(value, str) or value == "":
            raise ValueError(f"任务字段缺失或非法: {field_name}")

    if not isinstance(normalized["enabled"], bool):
        raise ValueError("任务字段缺失或非法: enabled")

    if normalized["quality"] not in QUALITIES:
        raise ValueError(f"未知 quality: {normalized['quality']}")

    if normalized["category"] not in CATEGORIES:
        raise ValueError(f"未知 category: {normalized['category']}")

    if normalized["slot"] not in SLOTS:
        raise ValueError(f"未知 slot: {normalized['slot']}")

    get_category_type_meta(normalized["category"], normalized["type"])


def build_task_slug(task):
    normalized = normalize_task(task)
    validate_task(normalized)
    return "-".join(
        (
            normalized["quality"],
            normalized["slot"],
            normalized["type"],
        )
    )


def describe_task(task):
    normalized = normalize_task(task)
    validate_task(normalized)

    return " ".join(
        (
            QUALITIES[normalized["quality"]]["label"],
            SLOTS[normalized["slot"]]["label"],
            CATEGORY_TYPES[normalized["category"]][normalized["type"]]["label"],
        )
    )

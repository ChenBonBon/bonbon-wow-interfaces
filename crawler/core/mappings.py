from copy import deepcopy


QUALITIES = {
    "uncommon": {"label": "绿色"},
    "rare": {"label": "蓝色"},
    "epic": {"label": "紫色"},
}

CATEGORIES = {
    "weapon": {"label": "武器"},
    "armor": {"label": "护甲"},
}

SLOTS = {
    "head": {"label": "头部"},
    "neck": {"label": "项链"},
    "shoulder": {"label": "肩部"},
    "cloak": {"label": "披风"},
    "chest": {"label": "胸部"},
    "wrist": {"label": "手腕"},
    "hands": {"label": "手部"},
    "waist": {"label": "腰部"},
    "legs": {"label": "腿部"},
    "feet": {"label": "脚部"},
    "finger": {"label": "戒指"},
    "trinket": {"label": "饰品"},
    "main_hand": {"label": "主手"},
    "off_hand": {"label": "副手"},
    "two_hand": {"label": "双手"},
    "ranged": {"label": "远程"},
}

CATEGORY_TYPES = {
    "weapon": {
        "dagger": {"label": "匕首"},
        "fist_weapon": {"label": "拳套"},
        "one_handed_axe": {"label": "单手斧"},
        "one_handed_mace": {"label": "单手锤"},
        "one_handed_sword": {"label": "单手剑"},
        "warglaive": {"label": "战刃"},
        "polearm": {"label": "长柄武器"},
        "staff": {"label": "法杖"},
        "two_handed_axe": {"label": "双手斧"},
        "two_handed_mace": {"label": "双手锤"},
        "two_handed_sword": {"label": "双手剑"},
        "bow": {"label": "弓"},
        "crossbow": {"label": "弩"},
        "gun": {"label": "枪械"},
        "wand": {"label": "魔杖"},
        "fishing_pole": {"label": "鱼竿"},
        "miscellaneous_weapon": {"label": "其他武器"},
    },
    "armor": {
        "cloth": {"label": "布甲"},
        "leather": {"label": "皮甲"},
        "mail": {"label": "锁甲"},
        "plate": {"label": "板甲"},
        "cosmetic": {"label": "幻化外观"},
        "shield": {"label": "盾牌"},
        "libram": {"label": "圣契"},
        "idol": {"label": "神像"},
        "totem": {"label": "图腾"},
        "sigil": {"label": "魔印"},
        "miscellaneous_armor": {"label": "其他护甲"},
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

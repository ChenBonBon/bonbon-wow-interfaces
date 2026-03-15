from copy import deepcopy


QUALITIES = {
    "uncommon_2": {
        "label": "绿色",
        "wowhead": {
            "facet": "quality",
            "value": 2
        }
    },
    "rare_3": {
        "label": "蓝色",
        "wowhead": {
            "facet": "quality",
            "value": 3
        }
    },
    "epic_4": {
        "label": "紫色",
        "wowhead": {
            "facet": "quality",
            "value": 4
        }
    }
}

QUERY_FILTER_VALUE_MAP = {
    "yes": 1,
    "no": 2,
    "any": None,
}

CATEGORIES = {
    "weapon": {
        "label": "武器",
        "wowhead": {
            "path": "weapons"
        }
    },
    "armor": {
        "label": "护甲",
        "wowhead": {
            "path": "armor"
        }
    }
}

SLOTS = {
    "head_1": {
        "label": "头部",
        "wowhead": {
            "facet": "slot",
            "value": 1
        }
    },
    "neck_2": {
        "label": "项链",
        "wowhead": {
            "facet": "slot",
            "value": 2
        }
    },
    "shoulder_3": {
        "label": "肩部",
        "wowhead": {
            "facet": "slot",
            "value": 3
        }
    },
    "shirt_4": {
        "label": "衬衣",
        "wowhead": {
            "facet": "slot",
            "value": 4
        }
    },
    "chest_5": {
        "label": "胸部",
        "wowhead": {
            "facet": "slot",
            "value": 5
        }
    },
    "waist_6": {
        "label": "腰部",
        "wowhead": {
            "facet": "slot",
            "value": 6
        }
    },
    "legs_7": {
        "label": "腿部",
        "wowhead": {
            "facet": "slot",
            "value": 7
        }
    },
    "feet_8": {
        "label": "脚部",
        "wowhead": {
            "facet": "slot",
            "value": 8
        }
    },
    "wrist_9": {
        "label": "手腕",
        "wowhead": {
            "facet": "slot",
            "value": 9
        }
    },
    "hands_10": {
        "label": "手部",
        "wowhead": {
            "facet": "slot",
            "value": 10
        }
    },
    "finger_11": {
        "label": "戒指",
        "wowhead": {
            "facet": "slot",
            "value": 11
        }
    },
    "trinket_12": {
        "label": "饰品",
        "wowhead": {
            "facet": "slot",
            "value": 12
        }
    },
    "one_hand_13": {
        "label": "单手",
        "wowhead": {
            "facet": "slot",
            "value": 13
        }
    },
    "shield_14": {
        "label": "盾牌",
        "wowhead": {
            "facet": "slot",
            "value": 14
        }
    },
    "ranged_15": {
        "label": "远程",
        "wowhead": {
            "facet": "slot",
            "value": 15
        }
    },
    "back_16": {
        "label": "披风",
        "wowhead": {
            "facet": "slot",
            "value": 16
        }
    },
    "two_hand_17": {
        "label": "双手",
        "wowhead": {
            "facet": "slot",
            "value": 17
        }
    },
    "tabard_19": {
        "label": "战袍",
        "wowhead": {
            "facet": "slot",
            "value": 19
        }
    },
    "main_hand_21": {
        "label": "主手",
        "wowhead": {
            "facet": "slot",
            "value": 21
        }
    },
    "off_hand_22": {
        "label": "副手",
        "wowhead": {
            "facet": "slot",
            "value": 22
        }
    },
    "held_in_off_hand_23": {
        "label": "持于副手",
        "wowhead": {
            "facet": "slot",
            "value": 23
        }
    },
    "ranged_26": {
        "label": "远程",
        "wowhead": {
            "facet": "slot",
            "value": 26
        }
    }
}

CATEGORY_TYPES = {
    "armor": {
        "shirts_-8": {
            "label": "衬衣",
            "wowhead": {
                "facet": "type",
                "value": -8
            }
        },
        "tabards_-7": {
            "label": "战袍",
            "wowhead": {
                "facet": "type",
                "value": -7
            }
        },
        "cloaks_-6": {
            "label": "披风",
            "wowhead": {
                "facet": "type",
                "value": -6
            }
        },
        "off_hand_frills_-5": {
            "label": "副手物品",
            "wowhead": {
                "facet": "type",
                "value": -5
            }
        },
        "trinkets_-4": {
            "label": "Trinkets",
            "wowhead": {
                "facet": "type",
                "value": -4
            }
        },
        "amulets_-3": {
            "label": "项链",
            "wowhead": {
                "facet": "type",
                "value": -3
            }
        },
        "rings_-2": {
            "label": "戒指",
            "wowhead": {
                "facet": "type",
                "value": -2
            }
        },
        "miscellaneous_armor_0": {
            "label": "其他护甲",
            "wowhead": {
                "facet": "type",
                "value": 0
            }
        },
        "cloth_armor_1": {
            "label": "布甲",
            "wowhead": {
                "facet": "type",
                "value": 1
            }
        },
        "leather_armor_2": {
            "label": "皮甲",
            "wowhead": {
                "facet": "type",
                "value": 2
            }
        },
        "mail_armor_3": {
            "label": "锁甲",
            "wowhead": {
                "facet": "type",
                "value": 3
            }
        },
        "plate_armor_4": {
            "label": "板甲",
            "wowhead": {
                "facet": "type",
                "value": 4
            }
        },
        "cosmetic_5": {
            "label": "幻化外观",
            "wowhead": {
                "facet": "type",
                "value": 5
            }
        },
        "shields_6": {
            "label": "盾牌",
            "wowhead": {
                "facet": "type",
                "value": 6
            }
        },
        "librams_7": {
            "label": "圣契",
            "wowhead": {
                "facet": "type",
                "value": 7
            }
        },
        "idols_8": {
            "label": "神像",
            "wowhead": {
                "facet": "type",
                "value": 8
            }
        },
        "totems_9": {
            "label": "图腾",
            "wowhead": {
                "facet": "type",
                "value": 9
            }
        },
        "sigils_10": {
            "label": "魔印",
            "wowhead": {
                "facet": "type",
                "value": 10
            }
        },
        "relics_11": {
            "label": "圣物",
            "wowhead": {
                "facet": "type",
                "value": 11
            }
        }
    },
    "weapon": {
        "one_handed_axes_0": {
            "label": "单手斧",
            "wowhead": {
                "facet": "type",
                "value": 0
            }
        },
        "two_handed_axes_1": {
            "label": "双手斧",
            "wowhead": {
                "facet": "type",
                "value": 1
            }
        },
        "bows_2": {
            "label": "弓",
            "wowhead": {
                "facet": "type",
                "value": 2
            }
        },
        "guns_3": {
            "label": "枪械",
            "wowhead": {
                "facet": "type",
                "value": 3
            }
        },
        "one_handed_maces_4": {
            "label": "单手锤",
            "wowhead": {
                "facet": "type",
                "value": 4
            }
        },
        "two_handed_maces_5": {
            "label": "双手锤",
            "wowhead": {
                "facet": "type",
                "value": 5
            }
        },
        "polearms_6": {
            "label": "长柄武器",
            "wowhead": {
                "facet": "type",
                "value": 6
            }
        },
        "one_handed_swords_7": {
            "label": "单手剑",
            "wowhead": {
                "facet": "type",
                "value": 7
            }
        },
        "two_handed_swords_8": {
            "label": "双手剑",
            "wowhead": {
                "facet": "type",
                "value": 8
            }
        },
        "warglaives_9": {
            "label": "战刃",
            "wowhead": {
                "facet": "type",
                "value": 9
            }
        },
        "staves_10": {
            "label": "法杖",
            "wowhead": {
                "facet": "type",
                "value": 10
            }
        },
        "fist_weapons_13": {
            "label": "拳套",
            "wowhead": {
                "facet": "type",
                "value": 13
            }
        },
        "miscellaneous_weapons_14": {
            "label": "其他武器",
            "wowhead": {
                "facet": "type",
                "value": 14
            }
        },
        "daggers_15": {
            "label": "匕首",
            "wowhead": {
                "facet": "type",
                "value": 15
            }
        },
        "thrown_16": {
            "label": "投掷武器",
            "wowhead": {
                "facet": "type",
                "value": 16
            }
        },
        "crossbows_18": {
            "label": "弩",
            "wowhead": {
                "facet": "type",
                "value": 18
            }
        },
        "wands_19": {
            "label": "魔杖",
            "wowhead": {
                "facet": "type",
                "value": 19
            }
        },
        "fishing_poles_20": {
            "label": "鱼竿",
            "wowhead": {
                "facet": "type",
                "value": 20
            }
        }
    }
}

QUERY_FILTERS = {
    "disenchantable_8": {
        "label": "可分解",
        "wowhead": {
            "id": 8
        },
        "values": {
            "yes": 1,
            "no": 2,
            "any": None
        }
    },
    "available_to_players_161": {
        "label": "玩家可用",
        "wowhead": {
            "id": 161
        },
        "values": {
            "yes": 1,
            "no": 2,
            "any": None
        }
    },
    "can_be_worn_equipped_195": {
        "label": "可穿戴/可装备",
        "wowhead": {
            "id": 195
        },
        "values": {
            "yes": 1,
            "no": 2,
            "any": None
        }
    }
}

QUERY_FILTER_ORDER = ("available_to_players_161", "can_be_worn_equipped_195", "disenchantable_8")

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

    if normalized["slot"] not in SLOTS:
        raise ValueError(f"未知 slot: {normalized['slot']}")

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

    return " ".join((
        QUALITIES[normalized["quality"]]["label"],
        SLOTS[normalized["slot"]]["label"],
        CATEGORY_TYPES[normalized["category"]][normalized["type"]]["label"],
    ))

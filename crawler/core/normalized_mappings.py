import json
from html.parser import HTMLParser
from pathlib import Path


TARGET_QUERY_FILTER_IDS = (8, 161, 195)
QUALITY_VALUES = (2, 3, 4)


class SelectOptionParser(HTMLParser):
    def __init__(self, select_id):
        super().__init__()
        self.select_id = select_id
        self.in_target_select = False
        self.in_option = False
        self.current_value = None
        self.current_label = []
        self.options = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "select" and attrs_dict.get("id") == self.select_id:
            self.in_target_select = True
            return

        if self.in_target_select and tag == "option":
            self.in_option = True
            self.current_value = attrs_dict.get("value")
            self.current_label = []

    def handle_data(self, data):
        if self.in_option:
            self.current_label.append(data)

    def handle_endtag(self, tag):
        if tag == "option" and self.in_option:
            label = "".join(self.current_label).strip()
            if self.current_value in (None, "") or label == "":
                raise ValueError(f"select {self.select_id} 中存在缺失 value 或 label 的 option")
            self.options.append({"value": int(self.current_value), "label": label})
            self.in_option = False
            self.current_value = None
            self.current_label = []
            return

        if tag == "select" and self.in_target_select:
            self.in_target_select = False


def extract_select_options(html_text, select_id):
    parser = SelectOptionParser(select_id)
    parser.feed(html_text)
    if not parser.options:
        raise ValueError(f"未找到 select: {select_id}")
    return parser.options


def extract_query_filters(filter_init_data):
    extracted = []
    filters = filter_init_data.get("filters", [])
    for filter_id in TARGET_QUERY_FILTER_IDS:
        filter_meta = next((item for item in filters if item.get("id") == filter_id), None)
        if filter_meta is None:
            raise ValueError(f"缺少 query filter: {filter_id}")

        values = []
        for option in filter_meta.get("options", []):
            if len(option) < 2 or option[0] is None:
                continue
            values.append({"value": int(option[0]), "label": str(option[1]).strip()})

        extracted.append(
            {
                "id": int(filter_meta["id"]),
                "label": str(filter_meta["name"]).strip(),
                "values": sorted(values, key=lambda item: item["value"]),
            }
        )

    return extracted


def _dedupe_options(*option_groups):
    merged = {}
    for options in option_groups:
        for option in options:
            value = option["value"]
            existing = merged.get(value)
            if existing is not None and existing != option:
                raise ValueError(f"同一 value 出现不一致定义: {value}")
            merged[value] = option
    return [merged[value] for value in sorted(merged)]


def build_normalized_mappings(armor_html, armor_filters, weapons_html, weapons_filters):
    armor_query_filters = extract_query_filters(armor_filters)
    weapons_query_filters = extract_query_filters(weapons_filters)
    if armor_query_filters != weapons_query_filters:
        raise ValueError("armor 与 weapons 的 query filter 定义不一致")

    qualities = [
        option
        for option in extract_select_options(armor_html, "filter-facet-quality")
        if option["value"] in QUALITY_VALUES
    ]

    return {
        "categories": {
            "armor": {"path": "armor"},
            "weapon": {"path": "weapons"},
        },
        "qualities": qualities,
        "slots": {
            "armor": sorted(
                extract_select_options(armor_html, "filter-facet-slot"),
                key=lambda item: item["value"],
            ),
            "weapon": sorted(
                extract_select_options(weapons_html, "filter-facet-slot"),
                key=lambda item: item["value"],
            ),
        },
        "types": {
            "armor": sorted(
                extract_select_options(armor_html, "filter-facet-type"),
                key=lambda item: item["value"],
            ),
            "weapon": sorted(
                extract_select_options(weapons_html, "filter-facet-type"),
                key=lambda item: item["value"],
            ),
        },
        "query_filters": armor_query_filters,
    }


def write_normalized_mappings(output_path, mappings):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(mappings, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path
